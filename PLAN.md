# Plan: Remove active_interview_context and leaf_coverage Tables

## Executive Summary

**Goal:** Simplify database schema by removing two tables while preserving all functionality.

**Key Changes:**
1. **Delete:** `active_interview_context` and `leaf_coverage` tables
2. **Add:** `summaries` table only (per-turn summaries for context management)
3. **Modify:** `life_areas` table gets `covered_at` timestamp column
4. **Architecture:** Shift from single summary per leaf to multiple summaries per leaf (better context management, solves overflow)

**Benefits:**
- Simpler schema (2 tables deleted, 1 added, net reduction!)
- Better context management (per-turn summaries instead of accumulating raw messages)
- Clearer coverage tracking (timestamp on leaf area itself instead of separate table)
- Same functionality preserved

**Complexity:** Medium
- ~9 files to modify
- New node in graph (`create_turn_summary`)
- New extraction worker for per-summary processing
- Modified evaluation logic (use summaries instead of raw messages)
- Data migration needed for existing coverage records

**Architecture Shift:**
- OLD: Interview → wait for leaf complete → batch extract all leaves in area
- NEW: Interview → extract EACH summary immediately → no waiting

---

## Current Understanding

### Tables to Remove
1. **`active_interview_context`** - Tracks current interview state per user
   - Stores: user_id, root_area_id, active_leaf_id, question_text, created_at
   - Purpose: Resume interviews when user reconnects
   - Used by: leaf interview subgraph, extract_target routing

2. **`leaf_coverage`** - Tracks progress and stores summaries
   - Stores: leaf_id, root_area_id, status, summary_text, vector, updated_at
   - Purpose: Progress tracking + summary/vector storage
   - Status values: 'pending', 'active', 'covered', 'skipped'
   - Used by: leaf interview, knowledge extraction, persistence

### Your Proposed Solutions

0. **Summaries**: New table with area_id, text, vector/embedding
   - Multiple summaries per leaf until fully covered

1. **Leaf Selection**: Exclude leaves with knowledge, traverse children in uuid7 order

2. **AI Question Persistence**: Already saved in history + leaf_history

3. **Completion Loop**: Return to start of subgraph to get next leaf

## Simplified Design (User Clarifications)

### ✅ Issue 1: When is a Leaf "Fully Covered"?
**Answer:** Simple - when `covered_at` IS NOT NULL
- No complex evaluation needed
- Quick_evaluate still determines when to set it

### ✅ Issue 2: Skipped Leaves
**Answer:** Set `covered_at` without creating summaries
- Doesn't matter that there are no summaries
- Same field handles both covered and skipped

### ✅ Issue 3: Extraction Happens Per-Summary
**Answer:** Extract EACH summary in background immediately!
- Summaries created during interview (synchronous)
- Knowledge extraction runs per-summary (async, triggered by new summary)
- NOT waiting for leaf to be covered
- Each summary independently processed

### ✅ Issue 4: Trigger Extraction
**Answer:** After creating ANY new summary
- Every turn that creates a summary → triggers background extraction
- Extraction worker processes that specific summary
- Adds vector and extracts knowledge from it

### ✅ Issue 5: Multiple Summaries Per Leaf
**Answer:** Keep collecting info until leaf marked covered
- Multiple turns = multiple summaries (don't lose info)
- Extraction can skip useless summaries
- Each summary optional for knowledge extraction

---

## User's Answers

### Q1: Completion Detection
**Answer:** Add `covered_at` timestamp to `life_areas` table
- `NULL` = needs interview (not covered)
- `NOT NULL` = covered (interview complete)

### Q2: Skipped Leaves
**Answer:** Set `covered_at` when skipped (with no summaries)

### Q3: Multiple Summaries
**Answer:** For context management:
- Each turn: question + answer → LLM → summary (save to DB)
- After quick_evaluate says "complete": aggregate all summaries → LLM → "is fully covered?"
- If YES: set `covered_at`
- Messages can be very long; summaries keep context manageable
- Can later vectorize and use for knowledge extraction

### Q4: Async Extraction
**Answer:** Use `covered_at` to exclude leaves (not knowledge/extracted_at)
- Leaf selection: exclude where `covered_at IS NOT NULL`
- Knowledge extraction timing: when all leaves have `covered_at` set

---

## Final Design

### Schema Changes

#### 1. DROP Tables
```sql
DROP TABLE active_interview_context;
DROP TABLE leaf_coverage;
```

#### 2. ADD Table: `summaries`
```sql
CREATE TABLE IF NOT EXISTS summaries (
    id TEXT PRIMARY KEY,              -- uuid7
    area_id TEXT NOT NULL,            -- which leaf area (FK to life_areas.id)
    summary_text TEXT NOT NULL,       -- 2-4 sentence summary of this turn
    vector TEXT,                       -- JSON embedding (nullable, added by extraction)
    created_at REAL NOT NULL          -- timestamp
);
CREATE INDEX idx_summaries_area_id ON summaries(area_id);
```

**Note:** Each summary gets its own vector during extraction. No consolidation needed.

#### 3. MODIFY Table: `life_areas`
```sql
ALTER TABLE life_areas ADD COLUMN covered_at REAL;
```
- `NULL` = not covered (needs interview)
- `NOT NULL` = covered (exclude from interviews)

#### 4. ~~ADD Table: `active_area`~~ **NOT NEEDED**

We don't need this table. Leaf selection is deterministic based on covered_at.

---

## How It Works

### A. Multiple Summaries Per Turn (Context Management)

**Problem:** Messages can be very long, overflow context window

**Solution:** Extract summary after each turn
1. User responds to question about leaf topic
2. Quick evaluate: "complete" | "partial" | "skipped"
3. Generate summary: question + answer → LLM → 2-4 sentence summary
4. Save to `summaries` table (no vector yet)
5. Accumulate summaries over multiple turns

### B. Coverage Detection

**After quick_evaluate returns "complete":**
1. Get all summaries for this leaf: `SELECT * FROM summaries WHERE area_id = ?`
2. Aggregate summaries → LLM: "Is this leaf topic fully covered?"
3. If YES: `UPDATE life_areas SET covered_at = ? WHERE id = ?`
4. If NO: Continue interviewing (generate follow-up)

**For "skipped" status:**
- Set `covered_at` immediately (no summaries needed)

### C. Leaf Selection Algorithm (Depth-First Traversal)

```python
async def get_next_uncovered_leaf(root_area_id: uuid.UUID) -> LifeArea | None:
    """Find next uncovered leaf using depth-first traversal.

    Algorithm:
    1. Start from root_area_id
    2. Get children (ordered by uuid7 id)
    3. Exclude children with covered_at IS NOT NULL
    4. Take first uncovered child
    5. If it has children (not a leaf), recurse into it
    6. If it's a leaf, return it
    7. If all leaves in branch covered, backtrack and try next sibling
    """
    async def _traverse(area_id: uuid.UUID) -> LifeArea | None:
        # Get immediate children
        children = await db.LifeAreasManager.get_children(area_id)

        # Filter out covered areas, order by id (uuid7)
        uncovered = [c for c in children if c.covered_at is None]
        uncovered.sort(key=lambda x: x.id)

        for child in uncovered:
            # Check if child has children (not a leaf)
            grandchildren = await db.LifeAreasManager.get_children(child.id)

            if grandchildren:
                # Not a leaf - recurse
                result = await _traverse(child.id)
                if result:
                    return result
            else:
                # Leaf found!
                return child

        # No uncovered leaves in this branch
        return None

    return await _traverse(root_area_id)
```

This replaces the flat list approach with proper tree traversal!

### D. Knowledge Extraction - Per Summary (Immediate!)

**Key Change:** Extract knowledge + vector from EACH summary immediately after creation!

**New Flow:**
```
User responds → create_turn_summary → save summary to DB
  ↓
Enqueue extraction task for THIS summary (background worker)
  ↓
Extraction worker processes THIS summary:
  - Generate vector
  - Extract knowledge (optional, can skip if useless)
  - Update summary.vector
  - Save knowledge items
```

**No waiting for leaf completion!** Each summary independently processed.

**Implementation:**
```python
# In create_turn_summary node
async def create_turn_summary(state: LeafInterviewState, llm: ChatOpenAI):
    """Generate and save summary, trigger extraction."""
    # ... generate summary ...

    # Save to DB
    summary_id = await db.SummariesManager.create(
        area_id=state.active_leaf_id,
        summary_text=summary_text,
    )

    # TRIGGER EXTRACTION for this specific summary
    await enqueue_summary_extraction(summary_id)

    return {"turn_summary_id": summary_id}

# Extraction worker (background process)
async def extract_summary_worker(summary_id: UUID):
    """Process ONE summary: generate vector + extract knowledge."""
    summary = await db.SummariesManager.get(summary_id)

    # Generate vector
    vector = await generate_embedding(summary.summary_text)

    # Extract knowledge (optional - skip if summary is useless)
    try:
        knowledge_items = await llm_extract_knowledge(summary.summary_text)
    except Exception:
        knowledge_items = []  # Skip if extraction fails

    # Save atomically
    async with transaction() as conn:
        # Update vector on THIS summary
        await db.SummariesManager.update_vector(summary_id, vector, conn=conn)

        # Save knowledge items
        for item in knowledge_items:
            kid = await db.UserKnowledgeManager.create(item, conn=conn)
            await db.UserKnowledgeAreasManager.create_link(
                kid, summary.area_id, conn=conn
            )
```

**Benefits:**
- Immediate processing (no waiting for leaf completion)
- Each summary gets its own vector
- Can skip useless summaries
- Simpler than batch processing

### F. Resuming Interviews

**No special tracking needed!** The routing flow already provides the area_id:

1. **extract_target** classifies intent and extracts area_id from user message
2. **leaf_interview subgraph** receives area_id in state
3. **load_interview_context** uses depth-first search to find next uncovered leaf

```python
async def load_interview_context(state: LeafInterviewState):
    """Find next uncovered leaf using depth-first traversal."""
    root_area_id = state.area_id  # From extract_target classification

    # Find next uncovered leaf (depth-first)
    next_leaf = await get_next_uncovered_leaf(root_area_id)

    if not next_leaf:
        # All leaves covered!
        return {"all_leaves_done": True}

    return {"active_leaf_id": next_leaf.id}
```

No active state tracking - selection is purely based on covered_at!

---

## Detailed Node Flow Changes

### Current Flow
```
quick_evaluate (uses raw messages)
  ↓
update_coverage_status (if complete: extract summary, prepare for save)
  ↓
select_next_leaf (find next where status not in covered/skipped)
  ↓
generate_leaf_response
  ↓
save_history (persist summary + status to leaf_coverage)
```

### New Flow
```
create_turn_summary (NEW: question + answer → summary → save to DB)
  ↓
quick_evaluate (MODIFIED: uses summaries instead of raw messages)
  ↓
update_coverage_status (MODIFIED: if complete, set covered_at)
  ↓
select_next_leaf (MODIFIED: find next where covered_at IS NULL)
  ↓
generate_leaf_response (unchanged)
  ↓
save_history (MODIFIED: persist covered_at to life_areas)
```

**Key Changes:**
1. **New node `create_turn_summary`**: Generates summary for this turn BEFORE evaluation
2. **Modified `quick_evaluate`**: Uses aggregated summaries instead of raw messages (solves context overflow)
3. **Modified `select_next_leaf`**: Checks `life_areas.covered_at` instead of `leaf_coverage.status`
4. **Modified `save_history`**: Updates `life_areas.covered_at` instead of `leaf_coverage`

### Prompt Changes

**New Prompt: `PROMPT_TURN_SUMMARY`**
```python
"""You are extracting a concise summary from a conversation turn.

Topic: {leaf_path}
Question: {question_text}
User Response: {user_message}

Extract a 2-4 sentence summary capturing what the user said about this topic.
Focus on facts, experiences, preferences, and concrete information.
"""
```

**Modified Prompt: `PROMPT_QUICK_EVALUATE` → `PROMPT_SUMMARY_EVALUATE`**
```python
"""You are evaluating whether a topic has been fully covered based on conversation summaries.

Topic: {leaf_path}

Conversation summaries:
{summaries}

Classify as:
- "complete": User has provided substantive information about this topic
- "partial": User started answering but needs more detail or clarification
- "skipped": User explicitly declined to discuss this topic

Return: status (complete/partial/skipped) and reason (brief explanation)
"""
```

---

## Implementation Steps

### 1. Database Migration (`src/infrastructure/db/schema.py`)

**Add:**
```python
# New summaries table
CREATE TABLE IF NOT EXISTS summaries (
    id TEXT PRIMARY KEY,
    area_id TEXT NOT NULL,
    summary_text TEXT NOT NULL,
    vector TEXT,
    created_at REAL NOT NULL
);
CREATE INDEX idx_summaries_area_id ON summaries(area_id);

# Alter life_areas
ALTER TABLE life_areas ADD COLUMN covered_at REAL;
```

**Drop:**
```python
DROP TABLE IF EXISTS active_interview_context;
DROP TABLE IF EXISTS leaf_coverage;
```

### 2. Create New Managers (`src/infrastructure/db/managers.py`)
```python
class SummariesManager:
    @staticmethod
    async def create(area_id: UUID, summary_text: str, conn=None) -> UUID

    @staticmethod
    async def list_by_area(area_id: UUID, conn=None) -> list[Summary]

    @staticmethod
    async def update_vector(summary_id: UUID, vector: list[float], conn=None)

# No ActiveAreaManager needed!
```

### 3. Update Leaf Interview Subgraph (`src/workflows/subgraphs/leaf_interview/nodes.py`)

**A. New Node: `create_turn_summary`**
```python
async def create_turn_summary(state: LeafInterviewState, llm: ChatOpenAI):
    """Generate summary for this conversation turn (deferred write)."""
    if not state.active_leaf_id or state.all_leaves_done:
        return {}

    # Get user's current message
    current_messages = filter_tool_messages(state.messages)
    if not current_messages:
        return {}

    user_message = normalize_content(current_messages[-1].content)

    # Get previous AI question from leaf_history (last AI message)
    leaf_messages = await db.LeafHistoryManager.get_messages(state.active_leaf_id)
    question_text = None
    if leaf_messages:
        # Last message in history is the AI's question
        for msg in reversed(leaf_messages):
            if msg.get("role") == "assistant":
                question_text = msg.get("content")
                break

    # Fallback to state.question_text if no history yet
    if not question_text:
        question_text = state.question_text or "Initial question about this topic"

    leaf_path = await get_leaf_path(state.active_leaf_id, state.area_id)

    # Generate summary
    prompt = PROMPT_TURN_SUMMARY.format(
        leaf_path=leaf_path,
        question_text=question_text,
        user_message=user_message,
    )
    messages = [SystemMessage(content=prompt), HumanMessage(content="Extract summary.")]
    response = await invoke_with_retry(lambda: llm.ainvoke(messages))
    summary_text = normalize_content(response.content)

    # Return summary in state for deferred persistence (written in save_history)
    logger.info("Generated turn summary", extra={"summary_len": len(summary_text)})
    return {"turn_summary_text": summary_text}
```

**B. Modified Node: `_get_next_uncovered_leaf`**
```python
async def _get_next_uncovered_leaf(
    area_id: uuid.UUID,
    leaf_areas: list[SubAreaInfo],
    exclude_ids: set[uuid.UUID] | None = None,
) -> SubAreaInfo | None:
    """Get first uncovered leaf using covered_at field."""
    # No more querying leaf_coverage!
    covered_ids = {
        info.area.id for info in leaf_areas
        if info.area.covered_at is not None
    }
    skip_ids = covered_ids | (exclude_ids or set())
    for info in leaf_areas:
        if info.area.id not in skip_ids:
            return info
    return None
```

**C. Modified Node: `quick_evaluate` (use summaries)**
```python
async def _evaluate_with_summaries(
    state: LeafInterviewState, llm: ChatOpenAI
) -> LeafEvaluation:
    """Evaluate coverage using summaries instead of raw messages."""
    # Get all summaries for this leaf
    summaries = await db.SummariesManager.list_by_area(state.active_leaf_id)

    if not summaries:
        # No summaries yet - first turn, can't be covered
        return LeafEvaluation(status="partial", reason="First turn, needs more info")

    # Aggregate summaries
    summary_texts = [s.summary_text for s in summaries]
    aggregated = "\n\n".join(summary_texts)

    leaf_path = await get_leaf_path(state.active_leaf_id, state.area_id)
    prompt = PROMPT_SUMMARY_EVALUATE.format(
        leaf_path=leaf_path,
        summaries=aggregated,
    )

    structured_llm = llm.with_structured_output(LeafEvaluation)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Evaluate coverage."},
    ]
    result = await invoke_with_retry(lambda: structured_llm.ainvoke(messages))
    return result

async def quick_evaluate(state: LeafInterviewState, llm: ChatOpenAI):
    """Evaluate if user has fully answered using summaries."""
    if state.all_leaves_done or not state.active_leaf_id:
        return {"leaf_evaluation": None, "is_successful": True}

    try:
        result = await _evaluate_with_summaries(state, llm)
    except Exception:
        logger.exception("Failed to evaluate with summaries")
        return {
            "leaf_evaluation": LeafEvaluation(
                status="partial", reason="Evaluation failed"
            )
        }

    logger.info("Evaluation complete", extra={"status": result.status})
    return {"leaf_evaluation": result}
```

**D. Modified Node: `update_coverage_status`**
```python
async def update_coverage_status(state: LeafInterviewState, llm: ChatOpenAI):
    """Set covered_at when complete or skipped."""
    if state.all_leaves_done or not state.active_leaf_id:
        return {"is_successful": True}

    evaluation = state.leaf_evaluation
    if evaluation and evaluation.status in ("complete", "skipped"):
        return {
            "completed_leaf_id": state.active_leaf_id,
            "set_covered_at": True,  # Signal to save_history to set covered_at
        }
    return {}
```

**E. Remove These Functions:**
- `_ensure_coverage_records` (no more coverage records to create)
- `_extract_leaf_summary` (replaced by per-turn summaries)
- `_create_leaf_context` (no more active_interview_context)

**F. Modified Function: `_get_leaf_areas_for_root`**
```python
async def _get_leaf_areas_for_root(area_id: uuid.UUID) -> list[SubAreaInfo]:
    """Get leaf areas for a root area."""
    descendants = await db.LifeAreasManager.get_descendants(area_id)
    leaf_areas = _get_leaf_areas(build_sub_area_info(descendants, area_id))
    # No more _ensure_coverage_records call!
    return leaf_areas
```

### 4. Update Persistence (`src/workflows/nodes/persistence/save_history.py`)

**A. New Function: `_save_turn_summary`**
```python
async def _save_turn_summary(state: SaveHistoryState, conn, now: float) -> None:
    """Save turn summary if present (deferred write from create_turn_summary)."""
    if not state.turn_summary_text or not state.active_leaf_id:
        return

    # Save summary to DB
    summary_id = await db.SummariesManager.create(
        area_id=state.active_leaf_id,
        summary_text=state.turn_summary_text,
        conn=conn
    )

    logger.info("Saved turn summary", extra={"summary_id": str(summary_id)})
```

**B. Modified: `_save_leaf_completion`**
```python
async def _save_leaf_completion(state: SaveHistoryState, conn, now: float) -> None:
    """Set covered_at when leaf is complete or skipped."""
    if not state.completed_leaf_id or not state.set_covered_at:
        return

    # Set covered_at timestamp
    await db.LifeAreasManager.set_covered_at(
        state.completed_leaf_id, now, conn=conn
    )
    logger.info("Set covered_at", extra={"leaf_id": str(state.completed_leaf_id)})
```

**C. Modified: `save_history`**
```python
async def save_history(state: SaveHistoryState) -> dict:
    messages_by_ts = state.messages_to_save or {}
    if not messages_by_ts:
        logger.debug("No messages to save", extra={"user_id": str(state.user.id)})
        return {}

    now = get_timestamp()
    async with transaction() as conn:
        await _save_messages(state, conn, now)
        await _save_turn_summary(state, conn, now)  # NEW: Save turn summary
        await _save_leaf_completion(state, conn, now)
        # _save_context_transition DELETED - no longer needed

    return {}
```

**D. Delete: `_save_context_transition`**

This function is no longer needed - no active_interview_context to save!

**C. New Manager Method Needed:**
```python
# In LifeAreasManager
@staticmethod
async def set_covered_at(area_id: UUID, timestamp: float, conn=None):
    """Set covered_at timestamp for a leaf area."""
    async with _get_connection(conn) as conn:
        await conn.execute(
            "UPDATE life_areas SET covered_at = ? WHERE id = ?",
            (timestamp, str(area_id)),
        )
```

### 5. ~~Update Extract Target~~ NO CHANGES NEEDED

**Current behavior is already correct:**
- extract_target classifies user intent and extracts area_id from message
- This area_id is passed to leaf_interview subgraph in state
- No tracking needed - the "active area" is whatever user is currently discussing

**Note:** The current override logic using `ActiveInterviewContextManager.get_by_user()` can be removed, but this is optional. The routing works fine without it since extract_target already classifies intent.

### 5. Update Leaf Interview Graph (`src/workflows/subgraphs/leaf_interview/graph.py`)

**Add new node to graph:**
```python
def build_leaf_interview_graph():
    graph = StateGraph(LeafInterviewState)

    # Add nodes
    graph.add_node("load_interview_context", load_interview_context)
    graph.add_node("create_turn_summary", create_turn_summary)  # NEW
    graph.add_node("quick_evaluate", quick_evaluate)
    graph.add_node("update_coverage_status", update_coverage_status)
    graph.add_node("select_next_leaf", select_next_leaf)
    graph.add_node("generate_leaf_response", generate_leaf_response)
    graph.add_node("completed_area_response", completed_area_response)

    # Add edges
    graph.add_edge(START, "load_interview_context")
    graph.add_conditional_edges("load_interview_context", route_after_context_load)
    graph.add_edge("create_turn_summary", "quick_evaluate")  # NEW
    graph.add_edge("quick_evaluate", "update_coverage_status")
    # ... rest of edges

    return graph.compile()
```

**Update router:**
```python
def route_after_context_load(state: LeafInterviewState) -> str:
    if state.area_already_extracted or state.all_leaves_done:
        return "completed_area_response"
    # NEW: Route to create_turn_summary instead of quick_evaluate
    return "create_turn_summary"
```

### 6. NEW: Summary Extraction Worker (`src/processes/extract/summary_worker.py`)

**New file for per-summary extraction:**
```python
async def extract_summary_worker(summary_id: UUID):
    """Background worker: extract knowledge + vector from ONE summary."""
    summary = await db.SummariesManager.get(summary_id)

    # Generate vector for this summary
    vector = await generate_embedding(summary.summary_text)

    # Try to extract knowledge (optional - can fail/skip)
    try:
        knowledge_items = await llm_extract_knowledge(
            summary.summary_text,
            summary.area_id
        )
    except Exception:
        logger.warning(f"Failed to extract knowledge from summary {summary_id}")
        knowledge_items = []

    # Save atomically
    async with transaction() as conn:
        # Update this summary's vector
        await db.SummariesManager.update_vector(
            summary_id, vector, conn=conn
        )

        # Save knowledge items
        for item in knowledge_items:
            kid = await db.UserKnowledgeManager.create(item, conn=conn)
            await db.UserKnowledgeAreasManager.create_link(
                kid, summary.area_id, conn=conn
            )

    logger.info(f"Extracted {len(knowledge_items)} items from summary {summary_id}")
```

**Trigger mechanism:**
```python
# In create_turn_summary node
async def create_turn_summary(...):
    # ... create summary ...

    # Enqueue extraction task
    await extraction_pool.submit(
        ExtractSummaryTask(summary_id=summary_id)
    )
```

**Note:** This replaces the current area-level knowledge extraction with per-summary extraction!

### 7. Update Command Handlers (`src/workflows/nodes/commands/handlers.py`)

**Modified: `_delete_area_data`**
```python
async def _delete_area_data(area_id: UUID, conn):
    """Delete area data when user resets."""
    # Get all leaves for this root area
    descendants = await db.LifeAreasManager.get_descendants(area_id)
    leaf_areas = _get_leaf_areas(build_sub_area_info(descendants, area_id))
    leaf_ids = [leaf.area.id for leaf in leaf_areas]

    # Delete summaries for all leaves
    for leaf_id in leaf_ids:
        await db.SummariesManager.delete_by_area(leaf_id, conn=conn)

    # Reset covered_at for all leaves
    for leaf_id in leaf_ids:
        await db.LifeAreasManager.set_covered_at(leaf_id, None, conn=conn)

    # Delete from other tables (knowledge, etc.)
    # ... existing deletion logic
```

### 8. Update State Models (`src/workflows/subgraphs/leaf_interview/state.py`)

**Add fields:**
```python
@dataclass
class LeafInterviewState:
    # ... existing fields ...

    # NEW: Track turn summary creation
    turn_summary_id: uuid.UUID | None = None

    # MODIFIED: Replace leaf_summary_text with set_covered_at flag
    set_covered_at: bool = False  # Signal to persist_state

    # REMOVE: These are no longer needed
    # leaf_summary_text: str | None = None  # DELETE
```

**Update SaveHistoryState:**
```python
@dataclass
class SaveHistoryState:
    # ... existing fields ...

    # NEW: Signal to set covered_at
    set_covered_at: bool = False

    # REMOVE: These are no longer needed
    # leaf_summary_text: str | None = None  # DELETE
```

### 9. Update Models (`src/infrastructure/db/models.py`)

**Add:**
```python
@dataclass
class Summary:
    """Summary of a conversation turn about a leaf area."""
    id: uuid.UUID
    area_id: uuid.UUID
    summary_text: str
    created_at: float
    vector: list[float] | None = None
    is_final: bool = False

@dataclass
class ActiveArea:
    """Current active interview area per user."""
    user_id: uuid.UUID
    root_area_id: uuid.UUID
    updated_at: float
```

**Modify:**
```python
@dataclass
class LifeArea:
    # ... existing fields ...
    covered_at: float | None = None  # NEW: When leaf was covered
```

**Remove:**
```python
# DELETE: ActiveInterviewContext
# DELETE: LeafCoverage
```

---

## Critical Files to Modify

1. **Schema & Models**
   - `src/infrastructure/db/schema.py` - add summaries, active_area; drop old tables; alter life_areas
   - `src/infrastructure/db/models.py` - add Summary, ActiveArea; remove old models; update LifeArea

2. **Managers**
   - `src/infrastructure/db/managers.py` - add SummariesManager, ActiveAreaManager; update LifeAreasManager

3. **Leaf Interview**
   - `src/workflows/subgraphs/leaf_interview/nodes.py` - new create_turn_summary node; modify quick_evaluate, update_coverage_status, select_next_leaf
   - `src/workflows/subgraphs/leaf_interview/graph.py` - add new node to graph
   - `src/workflows/subgraphs/leaf_interview/state.py` - update state fields

4. **Persistence**
   - `src/workflows/nodes/persistence/save_history.py` - modify _save_leaf_completion, _save_context_transition
   - `src/workflows/application/state.py` - update main state if needed

5. **Other Nodes**
   - `src/workflows/nodes/input/extract_target.py` - use ActiveAreaManager instead
   - `src/workflows/subgraphs/knowledge_extraction/nodes.py` - load from summaries table
   - `src/workflows/nodes/commands/handlers.py` - delete summaries, reset covered_at

6. **Prompts**
   - `src/shared/prompts.py` - add PROMPT_TURN_SUMMARY, PROMPT_SUMMARY_EVALUATE

---

## Data Migration Considerations

**For Existing Users:**
If there are active interviews in progress when this change deploys:

1. **Active Contexts:** Any active_interview_context records will be lost
   - **Impact:** Users will restart from first uncovered leaf
   - **Mitigation:** Acceptable for development; for production, migrate to active_area table

2. **Leaf Coverage:** Existing leaf_coverage records with status="covered" need migration
   - **Migration Script:**
   ```python
   # Read all covered/skipped leaves from leaf_coverage
   coverage_records = await db.LeafCoverageManager.list_all()

   for record in coverage_records:
       if record.status in ("covered", "skipped"):
           # Set covered_at on life_areas
           await db.LifeAreasManager.set_covered_at(
               record.leaf_id,
               record.updated_at
           )

           # Migrate summary if exists
           if record.summary_text:
               await db.SummariesManager.create(
                   area_id=record.leaf_id,
                   summary_text=record.summary_text,
                   is_final=True,  # Mark as final summary
                   vector=record.vector,
               )
   ```

3. **Testing Strategy:**
   - Test with fresh database first (no migration needed)
   - Then test migration script on copy of production DB
   - Verify all covered leaves properly marked

---

## Verification Plan

### Test Cases

1. **Basic interview flow with per-turn summaries**
   - Start interview on new area
   - Answer questions about leaves
   - **VERIFY:** Summary created and saved after EACH user response
   - **VERIFY:** Multiple summaries accumulate for same leaf
   - **VERIFY:** `covered_at` set when quick_evaluate returns "complete"

2. **Context management (multiple turns on same leaf)**
   - Give partial/incomplete answer
   - System asks follow-up (stays on same leaf)
   - Answer follow-up question
   - **VERIFY:** Multiple summary rows exist for this leaf
   - **VERIFY:** quick_evaluate uses aggregated summaries to determine coverage
   - **VERIFY:** Eventually marked covered when sufficient info provided

3. **Skipped topics**
   - Skip a leaf topic ("don't want to discuss")
   - **VERIFY:** `covered_at` set immediately
   - **VERIFY:** No summaries created (or empty summary)
   - **VERIFY:** Not asked again in next session

4. **Resume mid-interview**
   - Start interview, complete 2 leaves (multiple turns each)
   - Disconnect and reconnect
   - **VERIFY:** `active_area` table has correct root_area_id
   - **VERIFY:** Continues from next uncovered leaf (covered_at IS NULL)
   - **VERIFY:** Summaries from previous session still accessible

5. **Knowledge extraction with multi-turn summaries**
   - Complete all leaves in area (some with multiple turns/summaries)
   - **VERIFY:** Extraction worker triggered when all leaves have covered_at
   - **VERIFY:** load_area_data aggregates multiple summaries per leaf
   - **VERIFY:** Knowledge items created from aggregated summaries
   - **VERIFY:** Final summary row created with vector and is_final=1

6. **Multiple concurrent areas**
   - Start interview on Area A (complete 1 leaf)
   - Mid-interview, ask about Area B
   - **VERIFY:** `active_area` switches to Area B
   - Return to Area A
   - **VERIFY:** Resumes from next uncovered leaf in Area A

7. **Delete/reset area**
   - Complete some leaves in an area
   - Run delete/reset command
   - **VERIFY:** All summaries for those leaves deleted
   - **VERIFY:** `covered_at` reset to NULL
   - **VERIFY:** Can interview about these leaves again

### Manual Testing Commands
```bash
# Run all tests
make test

# Test specific components
uv run pytest tests/test_leaf_interview.py -v
uv run pytest tests/test_knowledge_extraction.py -v

# Run CLI for manual testing
make run-cli

# Test multi-turn conversation
# 1. Start interview on an area
# 2. Give partial answer (observe: summary created, stays on leaf)
# 3. Give more info (observe: another summary created)
# 4. Give complete info (observe: covered_at set, moves to next leaf)
# 5. Query DB to verify summaries table
```

### Database Inspection
```bash
# Check summaries table after testing
sqlite3 path/to/db.sqlite "SELECT area_id, summary_text, is_final FROM summaries ORDER BY created_at"

# Check covered_at timestamps
sqlite3 path/to/db.sqlite "SELECT id, title, covered_at FROM life_areas WHERE covered_at IS NOT NULL"

# Check active_area
sqlite3 path/to/db.sqlite "SELECT * FROM active_area"
```

---

## Design Decisions (Finalized)

### Q1: Vector Storage Strategy ✅
**Chosen:** Create one "final summary" row after aggregation with `is_final=1`
- Turn summaries: `is_final=0`, no vector
- Final summary: `is_final=1`, has vector
- Clean separation, no redundancy

### Q2: Active Area Management ✅
**Chosen:** Auto-update + cleanup
- Update `active_area` whenever interview route is taken
- Clear when area fully covered (all leaves have covered_at)
- Enables seamless resume and multi-area switching

### Q3: When to Create Turn Summary ✅
**Chosen:** After every user response, before evaluation
- New node `create_turn_summary` runs FIRST
- Then `quick_evaluate` uses all summaries to determine coverage
- Accumulates summaries even during partial responses
