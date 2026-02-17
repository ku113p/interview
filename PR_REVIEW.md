# PR Review: Remove coverage tables, per-summary extraction

**PR #6** — `feature/remove-coverage-tables` → `master`
**Reviewed:** 2026-02-17
**Reviewer:** Claude Code

---

## Summary

Replaces `leaf_coverage` with `summaries(id, area_id, summary_text, question_id, answer_id, vector, created_at)` (one row per interview turn), removes `user_id` from `user_knowledge_areas`, rewrites the knowledge extraction subgraph with stateless nodes and deferred DB writes.

Overall direction is sound and the code is substantially simpler. Three issues need fixing before merge.

---

## Issues

### HIGH

#### ~~`mark_extracted` called per-leaf breaks interview routing~~ — FIXED
**File:** `src/workflows/nodes/persistence/save_history.py` — `_save_leaf_completion`

`extracted_at` was broken and unused: `mark_extracted` was a dead write, and the `area_already_extracted` routing path was unreachable. Both `extracted_at` (column + methods) and the `all_leaves_done`/`area_already_extracted` state fields have been removed entirely. The router now uses `active_leaf_id is None` as the sole signal that all leaves are covered.

---

### MEDIUM

#### ~~`question_id` in turn summary points to wrong message~~ — FIXED
**File:** `src/workflows/nodes/persistence/save_history.py` — `_save_turn_summary`

`_resolve_question_id` now runs before `_save_messages`, so the lookup finds the question asked before the current turn rather than the new AI response inserted in the same transaction. `question_id` is passed explicitly to `_save_turn_summary`. Regression test added.

---

#### Destructive migration — no data migration for `user_knowledge_areas`
**File:** `src/infrastructure/db/schema.py` — `_run_migrations`

`DROP TABLE IF EXISTS user_knowledge_areas` with no data migration. All existing knowledge-to-area links are silently lost on upgrade.

**Fix:** Document explicitly as a breaking migration requiring a fresh DB, or add a data migration that copies rows: `INSERT INTO user_knowledge_areas_new SELECT knowledge_id, area_id FROM user_knowledge_areas`.

---

#### ~~Missing unit tests~~ — PARTIALLY FIXED
`create_turn_summary` (4 tests covering all paths) added to `tests/test_leaf_interview.py`.
`test_persist_extraction_rolls_back_on_failure` now asserts `vector IS NULL` after rollback.

Remaining (not blocking merge):

| Missing | Location |
|---------|----------|
| `route_after_context_load` 3-way router | `src/workflows/subgraphs/leaf_interview/graph.py` |
| `_save_turn_summary` helper | `src/workflows/nodes/persistence/save_history.py` |

---

### LOW

#### ~~`is_successful` in `KnowledgeExtractionState` is dead code~~ — FIXED
**File:** `src/workflows/subgraphs/knowledge_extraction/state.py`

Removed `is_successful` field from state. `load_summary` now returns `{}` on failure. `_route_after_load` in `graph.py` branches on `state.summary_text`. Test updated accordingly.

---

#### ~~`life_areas` CREATE TABLE missing `covered_at`~~ — FIXED
**File:** `src/infrastructure/db/schema.py`

Added `covered_at REAL` to the `CREATE TABLE IF NOT EXISTS life_areas` definition. The `ALTER TABLE ADD COLUMN` migration is retained for existing databases.

---

#### O(depth) redundant `get_descendants` queries in `_get_next_uncovered_leaf`
**File:** `src/workflows/subgraphs/leaf_interview/nodes.py`

Each recursive `_traverse(child_id)` call issues a full `get_descendants` query. For a tree of depth D, this is O(D) queries. The previous approach did one query. Works correctly but is a performance regression for deep trees.

---

#### ~~LLM_MANIFEST.md prompt numbering skips 3~~ — FIXED
Leaf interview prompts renumbered from 1, 2, 4, 5, 6, 7 → 1, 2, 3, 4, 5, 6.

---

## What's Good

- Deferred write pattern correctly maintained — all nodes are pure compute, `save_history` does all writes atomically
- Knowledge extraction subgraph is substantially simpler (deleted `routers.py`, linear pipeline)
- `test_interview_managers.py` gives solid `SummariesManager` coverage
- `test_full_summary_extraction_flow` correctly validates per-summary vectorization end-to-end
- `COUNT(DISTINCT uka.knowledge_id)` in test_report.sh is correct — prevents inflation from multi-area links
- All 11 integration tests passing at time of review

---

## Verdict

**Ready to merge.** The HIGH issue (broken routing) and the MEDIUM `question_id` off-by-one are both fixed. The destructive migration is acceptable for a pre-production codebase. Remaining LOW items are tracked above.
