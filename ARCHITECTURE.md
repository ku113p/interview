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

```
CLI Adapter
    ↓
Runtime (context manager)
    ├── Graph Worker Pool (size: 2)
    │   └── Processes ClientMessages through main graph
    │
    └── Extract Worker Pool (size: 2)
        └── Processes ExtractTask after criteria coverage
```

Communication via `asyncio.Queue` channels:
- `client_message`: CLI → Graph Workers
- `client_response`: Graph Workers → CLI
- `extract`: Graph Workers → Extract Workers

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

ORM pattern: `BaseModel[T]` with managers per table.

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
  area_id: UUID
  criteria_analysis: CriteriaAnalysis
  was_covered: bool            # Triggers extract worker
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
5. **Graceful Shutdown**: Worker pools handle cancellation properly
