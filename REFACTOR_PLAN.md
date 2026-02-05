# 🏗️ Complete Refactoring Plan - Option A (Minimal, Future-Ready)

## Executive Summary

This plan reorganizes your interview assistant codebase to improve maintainability, scalability, and prepare for future REST API, Telegram bot, and horizontal scaling features. **All changes are backward-compatible and minimize risk through incremental refactoring.**

---

## 📊 Current State Analysis

### File Statistics
- **Total Python files**: 41
- **Largest modules**: 
  - `db.py` (423 lines) - Database layer
  - `area_loop/tools.py` (248 lines) - LLM tools
  - `cli/session.py` (179 lines) - CLI interface
  - `interview.py` (123 lines) - Interview logic

### Key Issues Identified
1. **db.py is monolithic** - Mixes schema, connection management, ORM base classes, and 5 manager classes
2. **Root-level utility files scattered** - `ids.py`, `timestamp.py`, `message_buckets.py`, `config.py`, `logging_config.py`
3. **Nodes lack grouping** - All 6 workflow nodes in flat directory
4. **Configuration split** - Config and logging separated unnecessarily
5. **Subgraph inconsistency** - Different internal structures between `extract_flow` and `area_loop`

---

## 🎯 New Architecture (Option A - Minimal Refactoring)

### New Structure Overview

```
src/
├── config/                # 🆕 Centralized configuration
│   ├── __init__.py
│   ├── settings.py        # API keys, DB paths, constants
│   └── logging.py         # Logging configuration
│
├── domain/                # ✅ Business entities
│   ├── __init__.py
│   └── models.py          # Consolidated: User, Message, etc.
│
├── infrastructure/        # 🆕 External services & database
│   ├── __init__.py
│   ├── ai.py              # LLM client wrapper
│   └── db/
│       ├── __init__.py
│       ├── connection.py  # Connection management, transaction context
│       ├── schema.py      # SQLite table creation, migrations
│       └── repositories.py # Data access: UsersManager, HistoryManager, etc.
│
├── application/           # 🆕 Core orchestration
│   ├── __init__.py
│   ├── state.py           # LangGraph state definitions
│   └── graph.py           # Main workflow graph builder
│
├── workflows/             # 🆕 LangGraph-specific logic
│   ├── __init__.py
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── input/         # Input processing
│   │   │   ├── __init__.py
│   │   │   ├── build_user_message.py
│   │   │   └── extract_target.py
│   │   ├── processing/    # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── interview.py
│   │   │   └── load_history.py
│   │   └── persistence/   # Data saving
│   │       ├── __init__.py
│   │       └── save_history.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── message_router.py
│   │   └── history_router.py
│   └── subgraphs/
│       ├── __init__.py
│       ├── extract_flow/
│       │   ├── __init__.py
│       │   ├── graph.py
│       │   ├── state.py   # 🆕 Explicit state
│       │   └── nodes/
│       │       ├── __init__.py
│       │       ├── extract_audio.py
│       │       └── extract_text.py
│       └── area_loop/
│           ├── __init__.py
│           ├── graph.py
│           ├── state.py   # 🆕 Explicit state
│           ├── flow.py
│           ├── tools.py
│           └── nodes/
│               ├── __init__.py
│               ├── area_chat.py
│               ├── area_end.py
│               └── area_tools.py
│
├── adapters/              # 🆕 User interfaces
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── session.py
│   └── api/               # 🔮 Future REST API
│       └── __init__.py
│
└── shared/                # 🆕 Utilities & helpers
    ├── __init__.py
    ├── ids.py
    ├── timestamp.py
    ├── message_buckets.py
    └── utils/
        ├── __init__.py
        └── content.py
```

---

## 📝 Detailed Migration Steps

### Phase 1: Infrastructure Layer (Highest Priority)

#### Phase 1.1: Split `db.py` into `infrastructure/db/`
- `connection.py` - Connection management and transaction context
- `schema.py` - Schema definition and initialization
- `repositories.py` - ORM base class and manager classes

#### Phase 1.2: Create `config/` Module
- `settings.py` - API keys, DB paths, constants
- `logging.py` - Logging configuration (move from root)

### Phase 2: Shared Utilities
- Move `ids.py`, `timestamp.py`, `message_buckets.py` to `shared/`
- Move `utils/content.py` to `shared/utils/`

### Phase 3: Application & Workflows
- Move `state.py`, `graph.py` to `application/`
- Move `ai.py` to `infrastructure/`
- Reorganize `nodes/` into `workflows/nodes/{input,processing,persistence}/`
- Move `routers/` to `workflows/routers/`
- Move `subgraph/` to `workflows/subgraphs/` with state.py files

### Phase 4: Adapters
- Move `cli/` to `adapters/cli/`
- Create `adapters/api/` placeholder

### Phase 5: Domain Consolidation
- Merge `user.py` and `message.py` into `models.py`

---

## 📋 Import Changes Summary

| From | To |
|------|-----|
| `from src.db import` | `from src.infrastructure.db.repositories import` |
| `from src.config import` | `from src.config.settings import` |
| `from src.logging_config import` | `from src.config.logging import` |
| `from src.ai import` | `from src.infrastructure.ai import` |
| `from src.state import` | `from src.application.state import` |
| `from src.graph import` | `from src.application.graph import` |
| `from src.ids import` | `from src.shared.ids import` |
| `from src.timestamp import` | `from src.shared.timestamp import` |
| `from src.message_buckets import` | `from src.shared.message_buckets import` |
| `from src.utils.content import` | `from src.shared.utils.content import` |
| `from src.nodes.` | `from src.workflows.nodes.{input\|processing\|persistence}.` |
| `from src.routers.` | `from src.workflows.routers.` |
| `from src.subgraph.` | `from src.workflows.subgraphs.` |
| `from src.cli.` | `from src.adapters.cli.` |
| `from src.domain import user, message` | `from src.domain.models import User, Message` |

---

## 🧪 Testing Strategy

### After Each Phase:
1. **Manual smoke test**: `make run-cli --user-id <test-uuid>`
2. **Check imports**: `python -m src.application.graph` (should not error)
3. **Verify graph builds**: Try sending a message

### Validation Checklist:
- [ ] All Python files import successfully
- [ ] CLI starts without errors
- [ ] Can send a message and get a response
- [ ] Database writes work (check `interview.db`)
- [ ] History loads correctly

---

## ⚠️ Risk Mitigation

### Low-Risk Approach:
1. Create new directories first before moving files
2. Copy, don't move initially (delete old files after validation)
3. Work in feature branch: `refactor/restructure`
4. Commit after each phase for easy rollback
5. Keep `main.py` working at all times

### Rollback Plan:
```bash
git checkout main
git branch -D refactor/restructure
```

---

## 🚀 Future-Readiness (Option B Prep)

This refactoring sets you up perfectly for:

### REST API Addition:
```
src/adapters/api/
├── main.py             # FastAPI/Flask app
├── routes/
│   ├── interviews.py
│   ├── areas.py
│   └── users.py
└── middleware/
    └── auth.py
```

### Telegram Bot:
```
src/adapters/telegram/
├── bot.py
├── handlers/
│   ├── messages.py
│   └── commands.py
└── formatters/
    └── response.py
```

### Horizontal Scaling:
- Database connection pooling already in place
- LangGraph checkpointing can move to Redis
- API with Uvicorn workers
- Celery for async processing

---

## 📊 Estimated Effort

| Phase | Files Changed | Estimated Time | Risk |
|-------|---------------|----------------|------|
| 1. Infrastructure | 12 files | 2-3 hours | Medium |
| 2. Shared Utils | 15 files | 1 hour | Low |
| 3. Application/Workflows | 20 files | 2 hours | Medium |
| 4. Adapters | 3 files | 30 min | Low |
| 5. Domain Consolidation | 2 files | 30 min | Low |
| 5. Testing & Validation | All | 1-2 hours | - |
| **Total** | **~40 files** | **7-9 hours** | **Low-Medium** |

---

## ✅ Success Criteria

After refactoring, you should have:

1. **Cleaner imports**: No more scattered db/config imports
2. **Logical grouping**: Easy to find files by purpose
3. **Scalable structure**: Ready for API/bot/microservices
4. **Smaller files**: `db.py` split into 3 focused modules
5. **Better navigation**: Developers can find code intuitively
6. **Zero regressions**: All existing functionality works
