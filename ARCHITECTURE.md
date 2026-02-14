# Architecture

## Overview

Interview assistant using LangGraph for workflow orchestration. Collects structured information through conversation, manages hierarchical life areas (topics), and extracts knowledge from completed interviews. Sub-areas at any depth serve as interview topics for their ancestors.

## Layer Structure

```
src/
├── adapters/           # External interfaces (API)
├── processes/          # Independent async process modules
│   ├── auth/           # Auth worker (external ID → UUID)
│   ├── transport/      # CLI + Telegram transports
│   ├── interview/      # Main interview graph worker
│   └── extract/        # Knowledge extraction worker
├── runtime/            # Shared runtime infrastructure
├── config/             # Settings & model assignments
├── domain/             # Core business models
├── infrastructure/     # External services (LLM, database)
├── shared/             # Utilities & common types
└── workflows/          # LangGraph nodes, routers, subgraphs
```

### Layer Dependencies

```
adapters → processes → workflows → infrastructure → domain → shared
              ↓                                           ↘ config
           runtime
```

Each layer only imports from layers below it. Processes only import **interfaces** from other processes, never implementation.

## Main Workflow

```
START
  ↓
transcribe (subgraph)        # Convert audio/video to text
  ↓
handle_command ──(command)──→ END     # Handle /help, /clear, /delete, /mode
  │
  └─(continue)
      ↓
load_history                  # Load conversation from DB
  ↓
build_user_message           # Create HumanMessage
  ↓
extract_target               # Classify: conduct_interview | manage_areas | small_talk
  │
  ├─→ leaf_interview (subgraph)  # Interview flow
  │     ↓
  │   save_history → END
  │
  ├─→ area_loop (subgraph)   # CRUD for areas
  │     ↓
  │   save_history → END
  │
  └─→ small_talk_response    # Greetings, app questions, casual chat
        ↓
      save_history → END
```

### leaf_interview (subgraph)
Focused interview flow asking one leaf at a time.

```
START
  ↓
load_interview_context
  ├── Has active context? → load it
  └── No context? → pick first uncovered leaf, create context
  ↓
route_after_context_load
  ├─→ (all_leaves_done OR area_already_extracted) → completed_area_response → END
  └─→ quick_evaluate
        ↓
      update_coverage_status  # Mark leaf as covered/skipped
        ↓
      select_next_leaf        # Pick next uncovered leaf
        ↓
      generate_leaf_response → END
```

**Node details:**
- `load_interview_context`: Load/create active leaf context for user
- `quick_evaluate`: Evaluate user response (complete/partial/skipped)
- `update_coverage_status`: Mark leaf as covered/skipped; extracts and saves summary with embedding when covered
- `select_next_leaf`: Stay on current (partial) or pick next uncovered leaf
- `generate_leaf_response`: Generate focused question or transition message
- `completed_area_response`: Handle already-extracted areas

**Inline summary extraction:**
When a leaf is marked as "covered", `update_coverage_status` extracts a 2-4 sentence summary of the user's responses using `PROMPT_LEAF_SUMMARY`. The summary and its embedding vector are saved to `leaf_coverage.summary_text` and `leaf_coverage.vector`. This enables the knowledge extraction worker to use pre-extracted summaries instead of re-processing raw messages.

**Benefits:**
- O(1) token growth per turn (only current leaf + accumulated messages)
- Clearer, more focused questions
- Per-leaf coverage persistence
- Inline summary extraction (summaries available immediately when leaf completes)

## Command Handling

Commands are handled in the graph via `handle_command` node, making them transport-agnostic (works for CLI, Telegram, etc.).

| Command | Action |
|---------|--------|
| `/help` | Show available commands |
| `/clear` | Clear conversation history |
| `/delete` | Start account deletion (returns confirmation token) |
| `/delete_<token>` | Confirm deletion with token (deletes all user data) |
| `/mode` | Show current input mode |
| `/mode <name>` | Change mode (auto, interview, areas) |
| `/reset-area_<id>` | Start area reset (returns confirmation token) |
| `/reset-area_<token>` | Confirm reset (deletes summaries/knowledge, clears extracted_at) |
| `/exit`, `/exit_N` | CLI-only: Exit process (handled in transport) |

### Deletion Order (FK-safe)

When deleting a user, data is removed in this order:
1. `user_knowledge_areas` links
2. `user_knowledge` items
3. Per-area: `area_summaries`, `leaf_coverage`, `leaf_history`
4. `life_areas`
5. `histories`
6. `users`

### Token Storage

Delete and reset-area confirmation use time-limited tokens stored in module-level dicts:
- Token: 8-character hex string
- TTL: 60 seconds
- Delete storage: `dict[user_id, (token, timestamp)]`
- Reset-area storage: `dict[(user_id, area_id), (token, timestamp)]`

## Subgraphs

### transcribe
Handles media input processing.
- Routes by message type (text vs media)
- Converts video/audio to WAV
- Transcribes audio to text

### leaf_interview
Focused interview flow asking one leaf at a time. See [leaf_interview section](#leaf_interview-subgraph) above for flow diagram and node details.

**Key files:**
- `src/workflows/subgraphs/leaf_interview/graph.py` - Graph builder
- `src/workflows/subgraphs/leaf_interview/nodes.py` - Node implementations
- `src/workflows/subgraphs/leaf_interview/state.py` - LeafInterviewState model
- `src/workflows/subgraphs/leaf_interview/routers.py` - Routing logic

### area_loop
Tool-calling loop for hierarchical area management.
- `area_chat`: LLM with bound tools
- `area_tools`: Execute tool calls in transaction
- `area_end`: Finalize with success flag
- Max 10 iterations (recursion limit: 23)
- Sub-areas are created using `parent_id` to form a tree structure
- **Auto-set current area**: When creating a root area (no parent), it's automatically set as the user's `current_area_id`. This ensures the interview flow has a valid area immediately after creation.

### knowledge_extraction
Post-interview knowledge extraction (triggered when all leaves covered).
- `load_area_data`: Uses pre-extracted leaf_coverage summaries
- `extract_summaries`: Skipped when leaf summaries available (inline extraction already done)
- `save_summary`: Persist area-level summary with embedding
- `extract_knowledge`: Extract skills/facts
- `save_knowledge`: Persist knowledge items
- `mark_extracted`: Set `extracted_at` timestamp on area

## Process Architecture

The application is organized into 3 independent async processes that communicate through shared channels:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Transport  │    │    Auth     │    │  Interview  │    │   Extract   │
│ (CLI/Tg)    │◄──►│   Worker    │◄──►│   Workers   │◄──►│   Workers   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       └──────────────────┴──────────────────┴──────────────────┘
                              Channels (shared)
```

### Process Modules

| Module | Directory | Purpose | Exports |
|--------|-----------|---------|---------|
| auth | `src/processes/auth/` | Exchange external user IDs for internal user_ids | `run_auth_pool`, `AuthRequest`, `resolve_user_id` |
| transport | `src/processes/transport/` | CLI and Telegram transports | `run_cli`, `run_telegram`, `parse_user_id` |
| interview | `src/processes/interview/` | Main graph worker for message processing | `run_graph_pool`, `get_graph`, `State`, `Target` |
| extract | `src/processes/extract/` | Knowledge extraction from completed areas | `run_extract_pool`, `ExtractTask` |

### Runtime Infrastructure

Shared runtime utilities in `src/runtime/`:

| File | Purpose |
|------|---------|
| `channels.py` | Channels dataclass with all queue types |
| `pool.py` | Generic `run_worker_pool()` utility |

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
   - Graph worker queues `ExtractTask` when sub-areas covered
   - Extract workers process independently (fire-and-forget)

3. **Graceful Shutdown**:
   - Shared `shutdown` event signals all pools
   - Any pool can trigger (CLI `/exit`, SIGINT, etc.)
   - Workers check shutdown flag on each iteration

### Dependency Graph

```
main.py
    ├── src.runtime.Channels
    │
    ├── src.processes.auth
    │       └── interfaces.py (AuthRequest)
    │
    ├── src.processes.transport
    │       ├── imports src.processes.interview.interfaces
    │       └── imports src.processes.auth.interfaces
    │
    ├── src.processes.interview
    │       ├── interfaces.py (ChannelRequest, ChannelResponse)
    │       └── imports src.processes.extract.interfaces
    │
    └── src.processes.extract
            └── interfaces.py (ExtractTask)
```

Key: Each process only imports **interfaces** from other processes, never implementation.

### Key Files

| File | Purpose |
|------|---------|
| `processes/transport/cli.py` | CLI transport (stdin/stdout handling) |
| `processes/transport/telegram.py` | Telegram bot transport (polling/webhook) |
| `processes/auth/worker.py` | Auth worker (external ID → user_id) |
| `processes/interview/worker.py` | Graph worker pool |
| `processes/interview/graph.py` | Main LangGraph workflow |
| `processes/interview/state.py` | Main workflow state model |
| `processes/extract/worker.py` | Extract worker pool |
| `workflows/subgraphs/leaf_interview/graph.py` | Leaf interview subgraph |
| `workflows/subgraphs/leaf_interview/nodes.py` | Leaf interview node implementations |
| `runtime/channels.py` | Channel types and Channels dataclass |
| `runtime/pool.py` | Generic `run_worker_pool()` utility |

## Transports

Transports handle external communication (user I/O). Located in `src/processes/transport/`.

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

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | User profiles (id, mode, current_area_id) |
| `histories` | Conversation messages (JSON) |
| `life_areas` | Topics with hierarchy (parent_id, extracted_at timestamp when knowledge was extracted) |
| `leaf_history` | Join table linking leaves to their conversation messages |
| `area_summaries` | Extracted summaries + embeddings |
| `user_knowledge` | Skills/facts extracted |
| `user_knowledge_areas` | Knowledge-area links |
| `leaf_coverage` | Per-leaf interview coverage status (pending/active/covered/skipped) with summary + vector |
| `active_interview_context` | Current interview state per user (active leaf) |

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
  target: Target               # conduct_interview | manage_areas | small_talk
  messages: list[BaseMessage]  # Aggregated via add_messages
  messages_to_save: MessageBuckets
  is_successful: bool          # Operation success flag
  area_id: UUID
  coverage_analysis: AreaCoverageAnalysis
  is_fully_covered: bool       # All leaves covered, triggers extract worker
  command_response: str | None # Set when command handled (ends workflow early)
  area_already_extracted: bool # True if area has extracted_at set

  # Leaf interview state
  active_leaf_id: UUID | None     # Current leaf being asked about
  active_leaf_path: str | None    # Full path like "Work > Google > Responsibilities"
  leaf_evaluation: LeafEvaluation | None  # complete/partial/skipped
  question_text: str | None       # The question we asked
  all_leaves_done: bool           # True when all leaves covered/skipped
```

### Message Deduplication
`MessageBuckets` = `dict[float, list[BaseMessage]]` (timestamp → messages)

Merge function uses SHA-256 hash of (type, content, tool_calls) to prevent duplicates when subgraph inherits parent state.

## Model Assignments

| Node | Model | Purpose |
|------|-------|---------|
| extract_target | gpt-5.1-codex-mini | Fast intent classification |
| quick_evaluate | gpt-5.1-codex-mini | Evaluate user answer (complete/partial/skipped) |
| generate_leaf_response | gpt-5.1-codex-mini | Generate focused questions |
| leaf_summary | gpt-5.1-codex-mini | Extract summary from messages |
| area_chat | gpt-5.1-codex-mini | Tool-based area management |
| knowledge_extraction | gpt-5.1-codex-mini | Knowledge extraction |
| transcribe | gemini-2.5-flash-lite | Audio transcription |

Configured in `src/config/settings.py`. See `LLM_MANIFEST.md` for detailed token limits and temperatures.

## Key Patterns

1. **Structured LLM Output**: Pydantic models validate all LLM responses
2. **Transaction Safety**: Tool calls wrapped in DB transactions
3. **History Filtering**: ToolMessages filtered before chat LLM calls
4. **Temp File Cleanup**: Media files cleaned in finally blocks
5. **Graceful Shutdown**: Shared event signals all worker pools
6. **Correlation IDs**: Request/response matching for concurrent transports
7. **Peer Workers**: All pools are equal peers, no ownership hierarchy
8. **Interface Isolation**: Processes import only interfaces from each other
