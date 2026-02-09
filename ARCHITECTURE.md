# Architecture

## Overview

Interview assistant using LangGraph for workflow orchestration. Collects structured information through conversation, manages life areas (topics) with criteria, and extracts knowledge from completed interviews.

## Layer Structure

```
src/
├── adapters/           # External interfaces (API)
├── application/        # Workflow orchestration, transports & workers
├── config/             # Settings & model assignments
├── domain/             # Core business models
├── infrastructure/     # External services (LLM, database)
├── shared/             # Utilities & common types
└── workflows/          # LangGraph nodes, routers, subgraphs
```

### Layer Dependencies

```
adapters → application → workflows → infrastructure → domain → shared
                                                            ↘ config
```

Each layer only imports from layers below it.

## Main Workflow

```
START
  ↓
transcribe (subgraph)        # Convert audio/video to text
  ↓
load_history                  # Load conversation from DB
  ↓
build_user_message           # Create HumanMessage
  ↓
extract_target               # Classify: conduct_interview vs manage_areas
  ├─→ interview_analysis     # Check criteria coverage
  │     ↓
  │   interview_response     # Generate response
  │     ↓
  │   save_history → END
  │
  └─→ area_loop (subgraph)   # CRUD for areas/criteria
        ↓
      save_history → END
```

## Subgraphs

### transcribe
Handles media input processing.
- Routes by message type (text vs media)
- Converts video/audio to WAV
- Transcribes audio to text

### area_loop
Tool-calling loop for area/criteria management.
- `area_chat`: LLM with bound tools
- `area_tools`: Execute tool calls in transaction
- `area_end`: Finalize with success flag
- Max 10 iterations (recursion limit: 23)

### knowledge_extraction
Post-interview knowledge extraction (triggered when all criteria covered).
- `load_area_data`: Fetch area messages
- `extract_summaries`: LLM summarizes per criterion
- `save_summary`: Persist with embedding
- `extract_knowledge`: Extract skills/facts
- `save_knowledge`: Persist knowledge items

## Transports

Transports handle external communication (user I/O). Located in `src/application/transports/`.

| Transport | Purpose |
|-----------|---------|
| CLI | Handles stdin/stdout, user creation |
| Telegram | Bot interface via polling or webhook mode |

Transports are single async coroutines (not pools) that communicate with worker pools via channels.

### Telegram Transport

Supports two modes via `TELEGRAM_MODE` environment variable:
- **polling** (default): Long-polling for development/simple deployments
- **webhook**: HTTPS webhook for production

Required environment variables:
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather

Additional webhook variables:
- `TELEGRAM_WEBHOOK_URL`: Public HTTPS URL for webhook
- `TELEGRAM_WEBHOOK_HOST`: Bind address (default: 0.0.0.0)
- `TELEGRAM_WEBHOOK_PORT`: Port (default: 8443)
- `TELEGRAM_WEBHOOK_SECRET`: Optional secret token for verification

User ID mapping uses deterministic UUID5 from Telegram user ID, ensuring the same Telegram user always maps to the same internal user_id.

## Worker Architecture

Flat peer-based architecture where transports and worker pools communicate through shared channels:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Transport  │    │    Auth     │    │    Graph    │    │   Extract   │
│ (CLI/Tg)    │◄──►│   Worker    │◄──►│   Workers   │◄──►│   Workers   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       └──────────────────┴──────────────────┴──────────────────┘
                              Channels (shared)
```

### Worker Pools

| Pool | Size | Purpose |
|------|------|---------|
| Auth | 1 | Exchange external user IDs for internal user_ids |
| Graph | 2 | Processes messages through main graph |
| Extract | 2 | Knowledge extraction from covered areas |

### Channel Message Types

```python
ChannelRequest   # transport → graph (correlation_id, user_id, client_message)
ChannelResponse  # graph → transport (correlation_id, response_text)
ExtractTask      # graph → extract (area_id, user_id)
AuthRequest      # transport → auth (provider, external_id, display_name, response_future)
```

### Communication Flow

1. **Request/Response** (via correlation IDs):
   - Transport creates `ChannelRequest` with unique `correlation_id`
   - Graph worker processes, sends `ChannelResponse` with same `correlation_id`
   - Transport matches responses to pending requests by ID

2. **Background Extraction**:
   - Graph worker queues `ExtractTask` when criteria covered
   - Extract workers process independently (fire-and-forget)

3. **Graceful Shutdown**:
   - Shared `shutdown` event signals all pools
   - Any pool can trigger (CLI `/exit`, SIGINT, etc.)
   - Workers check shutdown flag on each iteration

### Key Files

| File | Purpose |
|------|---------|
| `transports/cli.py` | CLI transport (stdin/stdout handling) |
| `transports/telegram.py` | Telegram bot transport (polling/webhook) |
| `workers/channels.py` | Channel types and Channels dataclass |
| `workers/auth_worker.py` | Auth worker (external ID → user_id) |
| `workers/graph_worker.py` | Graph worker pool |
| `workers/extract_worker.py` | Extract worker pool |
| `workers/pool.py` | Generic `run_worker_pool()` utility |

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | User profiles (id, mode, current_area_id) |
| `histories` | Conversation messages (JSON) |
| `life_areas` | Topics with hierarchy (parent_id) |
| `criteria` | Evaluation criteria per area |
| `life_area_messages` | Interview responses per area |
| `area_summaries` | Extracted summaries + embeddings |
| `user_knowledge` | Skills/facts extracted |
| `user_knowledge_areas` | Knowledge-area links |

ORM pattern: `ORMBase[T]` with managers per table. Database managers are exported from `src/infrastructure/db/managers.py`.

### Async Database Layer

The database layer uses `aiosqlite` for async SQLite access with WAL mode for multi-client concurrent access:

```python
PRAGMA journal_mode = WAL     # Write-Ahead Logging
PRAGMA busy_timeout = 30000   # 30 second retry on lock contention
```

**Key benefits:**
- WAL mode allows multiple simultaneous readers
- Single writer doesn't block readers (writes go to separate `-wal` file)
- `busy_timeout` automatically retries on `SQLITE_BUSY` instead of failing
- Works across multiple processes accessing the same `.db` file

**Connection patterns:**
```python
# Simple read/write
async with get_connection() as conn:
    cursor = await conn.execute(query, params)
    row = await cursor.fetchone()

# Transaction with automatic rollback
async with transaction() as conn:
    await conn.execute(insert_query, values)
    # Commits on success, rolls back on exception
```

**Retry logic for write contention:**

Under parallel load, SQLite write transactions can fail with `SQLITE_BUSY` or `database is locked` errors despite the `busy_timeout` setting. The `transaction()` context manager automatically retries commits using exponential backoff:

| Setting | Value | Description |
|---------|-------|-------------|
| Max retries | 5 | Maximum retry attempts |
| Initial wait | 100ms | First retry delay |
| Max wait | 2s | Maximum retry delay |
| Jitter | 10% | Random variance to prevent thundering herd |

The `execute_with_retry()` utility in `connection.py` handles this using the `tenacity` library. It only retries on `sqlite3.OperationalError` containing "locked" or "busy" in the message.

**Cross-process file locking:**

Both `get_connection()` and `transaction()` use file-based locking (`fcntl.flock`) to serialize database access across processes. This prevents concurrent writes from conflicting:

- Lock file: `{db_path}.lock` (e.g., `interview.db.lock`)
- Lock type: Exclusive (`LOCK_EX`) - only one holder at a time
- Blocking: Callers wait until lock is available
- Cleanup: Lock file is deleted after release
- Platform: Linux/Unix only (`fcntl` module)

The `transaction()` context manager also uses an in-process `asyncio.Lock` for faster serialization when multiple coroutines run in the same process.

All ORM methods (`get_by_id`, `list`, `create`, `update`, `delete`) are async.

## State Models

### Main Graph State
```python
State:
  user: User
  message: ClientMessage
  text: str                    # Extracted text
  target: Target               # conduct_interview | manage_areas
  messages: list[BaseMessage]  # Aggregated via add_messages
  messages_to_save: MessageBuckets
  is_successful: bool          # Operation success flag
  area_id: UUID
  criteria_analysis: CriteriaAnalysis
  is_fully_covered: bool       # All criteria covered, triggers extract worker
```

### Message Deduplication
`MessageBuckets` = `dict[float, list[BaseMessage]]` (timestamp → messages)

Merge function uses SHA-256 hash of (type, content, tool_calls) to prevent duplicates when subgraph inherits parent state.

## Model Assignments

| Node | Model | Purpose |
|------|-------|---------|
| extract_target | gemini-2.5-flash-lite | Fast intent classification |
| interview_analysis | gemini-2.5-flash | Criteria coverage check |
| interview_response | gpt-5.1 | Response generation |
| area_chat | gemini-2.5-flash | Tool-based area management |
| knowledge_extraction | gemini-2.5-flash | Knowledge extraction |

Configured in `src/config/settings.py`.

## Key Patterns

1. **Structured LLM Output**: Pydantic models validate all LLM responses
2. **Transaction Safety**: Tool calls wrapped in DB transactions
3. **History Filtering**: ToolMessages filtered before chat LLM calls
4. **Temp File Cleanup**: Media files cleaned in finally blocks
5. **Graceful Shutdown**: Shared event signals all worker pools
6. **Correlation IDs**: Request/response matching for concurrent transports
7. **Peer Workers**: All pools are equal peers, no ownership hierarchy
