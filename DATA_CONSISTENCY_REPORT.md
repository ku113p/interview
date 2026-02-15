# Data Consistency Inspection Report

## Executive Summary

The codebase has a fundamentally sound architecture with good transaction usage in most critical paths. However, there are **5 concrete bugs/risks** related to partial saves and missing transaction boundaries. The issues are fixable within the current architecture — no language change or major rewrite needed.

---

## Part 1: Concrete Issues Found

### Issue 1 (HIGH) — `save_knowledge` uses `get_connection()` instead of `transaction()`

**File**: `src/workflows/subgraphs/knowledge_extraction/knowledge_nodes.py:150`

```python
async with get_connection() as conn:          # <-- no automatic rollback!
    for item in state.extracted_knowledge:
        await db.UserKnowledgeManager.create(...)
        await db.UserKnowledgeAreasManager.create_link(...)
    await conn.commit()                        # <-- manual commit
```

**Problem**: If an exception occurs after saving 3 out of 5 knowledge items (e.g., a unique constraint violation, LLM returned malformed data for item 4), the first 3 items are already written. The `get_connection()` context manager does NOT rollback on exception — it just closes the connection. Result: **partial knowledge saved**, and since `mark_area_extracted` runs AFTER this node, the area won't be marked as extracted, but orphaned knowledge rows exist.

**Fix**: Change `get_connection()` to `transaction()`.

---

### Issue 2 (HIGH) — `update_coverage_status` performs two independent saves without a transaction

**File**: `src/workflows/subgraphs/leaf_interview/nodes.py:303-322`

```python
async def _mark_leaf_complete(state, evaluation, llm):
    now = get_timestamp()
    status = "covered" if evaluation.status == "complete" else "skipped"

    if status == "covered":
        try:
            await _save_leaf_summary(state, llm, now)     # STEP 1: save summary + vector
        except Exception:
            logger.exception(...)                          # swallowed!

    await db.LeafCoverageManager.update_status(...)        # STEP 2: mark as covered
```

**Problem**: Two scenarios:
1. **Summary save succeeds, status update fails**: Summary is saved but leaf stays "active". Next turn, the system tries to re-evaluate the same leaf. Not catastrophic but wastes an LLM call and could produce duplicate summaries.
2. **Summary save fails (swallowed), status updates to "covered"**: Leaf is marked covered **without a summary**. When knowledge extraction runs, it expects summaries from covered leaves. It gets nothing, so the entire area's extraction may produce empty/degraded output.

Scenario 2 is the worse one — the `try/except` swallowing on line 311-314 silently degrades data quality.

---

### Issue 3 (MEDIUM) — Main workflow: mid-subgraph crash loses messages but keeps DB state changes

**Graph flow**:
```
leaf_interview subgraph:
  load_interview_context  [WRITES: active_interview_context, leaf_coverage]
  → quick_evaluate        [no writes]
  → update_coverage_status [WRITES: leaf_coverage status, summary]
  → select_next_leaf      [WRITES: active_interview_context, leaf_coverage]
  → generate_leaf_response [WRITES: active_interview_context.question_text]
                            ↓
save_history               [WRITES: histories, leaf_history]
```

**Problem**: Each node writes independently. If the process crashes between `update_coverage_status` and `save_history`:
- Leaf is marked "covered" in `leaf_coverage`
- `active_interview_context` points to the next leaf
- But the user's answer and AI's response are **never saved to `histories`**
- The `leaf_history` link is never created

**Result**: The leaf summary was extracted from messages that include the current turn (via `accumulate_with_current`), but those messages themselves are lost. The system moves to the next leaf as if everything is fine, but there's a gap in conversation history.

This is the classic "distributed write" problem within a single-process pipeline.

---

### Issue 4 (MEDIUM) — Knowledge extraction pipeline: three sequential saves with no atomicity

**File**: `src/workflows/subgraphs/knowledge_extraction/graph.py:25-28`

```
save_summary → extract_knowledge → save_knowledge → mark_extracted
```

Each node saves independently:
1. `save_summary` — writes `area_summaries` (no transaction)
2. `save_knowledge` — writes `user_knowledge` + `user_knowledge_areas` (no transaction, see Issue 1)
3. `mark_area_extracted` — writes `life_areas.extracted_at`

**Problem**: If `save_knowledge` fails after `save_summary` succeeds:
- Summary exists in `area_summaries`
- Knowledge is partially or not saved
- Area is NOT marked as extracted
- There's no retry mechanism — the extract task just logs the error and the worker moves on
- The area can never be re-extracted without manually running `/reset-area`

**Worse**: Even if the user runs `/reset-area`, it deletes `area_summaries` and `leaf_coverage` data but doesn't clean up `user_knowledge` rows (those are only cleaned in `/delete` full account deletion).

---

### Issue 5 (LOW) — Extract task queue is in-memory only

**File**: `src/processes/interview/worker.py:65-71`

```python
async def _enqueue_extract_if_leaf_completed(result, channels):
    completed_leaf_id = result.get("completed_leaf_id")
    if completed_leaf_id:
        task = ExtractTask(area_id=completed_leaf_id)
        await channels.extract.put(task)
```

The extract task queue is an `asyncio.Queue` — purely in-memory. If the process crashes after `save_history` commits but before the extract worker processes the task, the extraction is silently lost. The leaf is marked "covered" but extraction never runs.

---

## Part 2: Architectural Analysis

### What you have now: "Manual Saga" pattern

The current architecture is effectively an **orchestrated saga without compensating transactions**. Each LangGraph node is a saga step that does its own persistence. The problem: when a step fails, there's no undo for previous steps.

### Pattern comparison for this case

| Pattern | Fits this case? | Why / Why not |
|---------|----------------|---------------|
| **SQLite transactions** | YES — for adjacent writes | Already used well in most places. Issues 1-2 are just missed spots. |
| **LangGraph Checkpointing** | YES — best ROI fix | Adds crash recovery. If a node fails, LangGraph can resume from the last checkpoint. Uses `SqliteSaver` — minimal code change. |
| **Saga + compensating TXs** | OVERKILL | Single DB. Sagas solve cross-service consistency. All nodes write to the same SQLite. |
| **Event Sourcing** | OVERKILL | No need for time-travel or audit trails. CRUD is appropriate. |
| **Temporal / Durable Execution** | OVERKILL | Solves the right problem but requires running infrastructure (Temporal server). LangGraph checkpointing gives 80% of the benefit. |
| **Outbox pattern** | PARTIALLY relevant | The `ExtractTask` channel queue is an in-memory outbox. A DB-backed task queue would fix Issue 5. |
| **Rust typestate** | NOT NEEDED | Compile-time state machine enforcement is elegant, but Pydantic models + LangGraph routing already enforce valid transitions at runtime. |

### Recommended approach: Two-tier fix

**Tier 1 — Fix the bugs (immediate, low effort)**:
1. Change `save_knowledge` to use `transaction()` instead of `get_connection()`
2. Wrap `_mark_leaf_complete` in a transaction (summary save + status update together), or at minimum don't swallow the summary error — let it fail the node so the leaf isn't falsely marked as covered
3. Ensure `/reset-area` also cleans `user_knowledge` + `user_knowledge_areas`

**Tier 2 — Add LangGraph checkpointing (medium effort, high value)**:
```python
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

checkpointer = AsyncSqliteSaver.from_conn_string("interview_checkpoints.db")
graph = builder.compile(checkpointer=checkpointer)
```

This gives:
- **Crash recovery**: If the process dies mid-pipeline, next invocation with the same `thread_id` resumes from the last checkpoint
- **No partial state**: Each super-step is atomic from LangGraph's perspective
- **Time-travel debugging**: Inspect any historical state

The key design change: instead of each node writing to the DB independently, nodes would **return state updates** and a single "commit" node at the end would persist everything. This is the "collect-then-commit" pattern — `save_history` already does this for messages. The same approach could be extended to coverage updates.

### Regarding Rust/Go

Not necessary. The consistency issues are architectural (write ordering, transaction boundaries), not language-level. Python + SQLite + LangGraph is the right stack for this project's scale. Rust's typestate pattern is elegant but Pydantic + LangGraph routing achieves the same thing at runtime. The only advantage Go/Rust would give is fearless concurrency — but the write serialization via `fcntl.flock` + `asyncio.Lock` already handles this correctly.

What WOULD justify a language change:
- Handling 1000+ concurrent interviews (Go's goroutines or Rust's tokio would outperform Python's asyncio)
- Moving to PostgreSQL with connection pooling at scale
- Needing sub-millisecond response times

None of these apply to the current project.

---

## Part 3: Summary of all DB writes and their safety

| Operation | Location | Transaction? | Rollback? | Risk |
|-----------|----------|-------------|-----------|------|
| `save_history` (messages + leaf links) | `save_history.py:64` | YES | YES | SAFE |
| `_create_leaf_context` (context + coverage) | `leaf_interview/nodes.py:132` | YES | YES | SAFE |
| `_transition_to_next_leaf` (context + coverage) | `leaf_interview/nodes.py:346` | YES | YES | SAFE |
| `_ensure_coverage_records` (coverage) | `leaf_interview/nodes.py:56-67` | NO | NO | LOW — INSERT OR IGNORE, idempotent |
| `_mark_leaf_complete` (summary + status) | `leaf_interview/nodes.py:303` | NO | NO | **BUG** — summary error swallowed |
| `_update_leaf_context` (question text) | `leaf_interview/nodes.py:422` | NO | NO | LOW — non-critical metadata |
| `area_tools` (CRUD) | `area_loop/nodes.py` | YES | YES | SAFE |
| `save_summary` (area summary) | `knowledge_extraction/nodes.py:275` | NO | NO | MEDIUM — orphan if next step fails |
| `save_knowledge` (knowledge + links) | `knowledge_nodes.py:150` | NO | NO | **BUG** — partial writes possible |
| `mark_area_extracted` (timestamp) | `knowledge_extraction/nodes.py:291` | NO | NO | LOW — single UPDATE |
| `/delete` (full cascade) | `handlers.py` | YES | YES | SAFE |
| `/clear` (history) | `handlers.py` | YES | YES | SAFE |
| `/reset-area` | `handlers.py` | YES | YES | SAFE — but missing knowledge cleanup |

---

## Part 4: SQLite/aiosqlite Specifics

### Current locking strategy (GOOD)

The project implements a robust three-layer defense in `src/infrastructure/db/connection.py`:

```
Layer 1: fcntl.flock  (cross-process exclusive lock on .lock file)
Layer 2: asyncio.Lock (_transaction_lock, in-process serialization)
Layer 3: execute_with_retry (tenacity retry on SQLITE_BUSY/LOCKED)
```

### WAL mode limitations

WAL mode enables concurrent reads while a write is in progress, but does **not** enable concurrent writes. There is still a single writer at any time. The dual-locking strategy correctly serializes writes.

### aiosqlite note

aiosqlite is not true async I/O — it wraps synchronous `sqlite3` using a background thread per connection. Each connection occupies one OS thread. This is fine at the current scale but worth knowing for future scaling decisions.
