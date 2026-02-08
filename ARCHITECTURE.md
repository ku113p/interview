# Architecture

## Overview

Interview assistant using LangGraph for workflow orchestration. Collects structured information through conversation, manages life areas (topics) with criteria, and extracts knowledge from completed interviews.

## Layer Structure

```
src/
├── adapters/           # External interfaces (CLI, API)
├── application/        # Workflow orchestration & workers
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
extract_target               # Classify: interview vs areas
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

## Worker Architecture

Flat peer-based architecture where all worker pools communicate through shared channels:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Transport  │    │    Graph    │    │   Extract   │
│   Workers   │◄──►│   Workers   │◄──►│   Workers   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                    Channels (shared)
```

### Worker Pools

| Pool | Size | Purpose |
|------|------|---------|
| Transport (CLI) | 1 | Handles stdin/stdout, user creation |
| Graph | 2 | Processes messages through main graph |
| Extract | 2 | Knowledge extraction from covered areas |

### Channel Message Types

```python
ChannelRequest   # transport → graph (correlation_id, user_id, payload)
ChannelResponse  # graph → transport (correlation_id, payload)
ExtractTask      # graph → extract (area_id, user_id)
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
| `channels.py` | Channel types and Channels dataclass |
| `cli_worker.py` | CLI worker pool (stdin/stdout handling) |
| `graph_worker.py` | Graph worker pool |
| `extract_worker.py` | Extract worker pool |
| `pool.py` | Generic `run_worker_pool()` utility |

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

## State Models

### Main Graph State
```python
State:
  user: User
  message: ClientMessage
  text: str                    # Extracted text
  target: Target               # interview | areas
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
