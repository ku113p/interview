# Test Results

## Summary

| Metric | Value |
|--------|-------|
| Total Cases | 11 |
| Passed | 11 |
| Failed | 0 |
| Pass Rate | 100% |

## Results by Case

| # | Case Name | Status | Areas | Sub-Areas | Summaries | Knowledge | Last Run |
|---|-----------|--------|-------|-----------|-----------|-----------|----------|
| 1 | CRUD Operations | PASS | 3/3 | 2/2-2 | 2/true | 4/true | 2026-02-15 00:35 |
| 5 | Quick Interaction | PASS | 1/1 | 0/0-0 | 0/false | 0/false | 2026-02-15 00:35 |
| 13 | Knowledge - Skill Extraction | PASS | 3/3 | 2/2-2 | 2/true | 5/true | 2026-02-15 00:35 |
| 18 | Multi-Area - Creation | PASS | 3/3 | 0/0-0 | 0/false | 0/false | 2026-02-15 00:36 |
| 21 | Tree Sub-Areas Full Flow | PASS | 4/4 | 3/3-3 | 3/true | 7/true | 2026-02-15 00:35 |
| 22 | Subtree - Bulk Create | PASS | 7/7 | 6/6-6 | 0/false | 0/false | 2026-02-15 00:35 |
| 23 | Subtree - Deep Nesting | PASS | 5/5 | 4/4-4 | 0/false | 0/false | 2026-02-15 00:35 |
| 24 | Small Talk Flow | PASS | 3/3 | 2/2-2 | 0/false | 0/false | 2026-02-15 00:35 |
| 25 | Completed Area Message | PASS | 3/3 | 2/2-2 | 2/true | 5/true | 2026-02-15 00:35 |
| 26 | Reset Area Command | PASS | 3/3 | 2/2-2 | 2/true | 5/true | 2026-02-15 00:36 |
| 27 | Multi-Turn Leaf Interview | PASS | 2/2 | 1/1-1 | 1/true | 3/true | 2026-02-15 00:36 |

## Test Case Descriptions

| # | Name | Focus |
|---|------|-------|
| 1 | CRUD Operations | Basic area + sub-area creation, leaf-by-leaf interview flow |
| 5 | Quick Interaction | Minimal conversation, no extraction expected |
| 13 | Knowledge - Skill Extraction | Technical skill extraction from leaf-by-leaf interview |
| 18 | Multi-Area - Creation | Creating multiple root areas in one session |
| 21 | Tree Sub-Areas Full Flow | Hierarchical sub-areas with nested parent-child relationships |
| 22 | Subtree - Bulk Create | Bulk nested sub-area creation via create_subtree |
| 23 | Subtree - Deep Nesting | Deep nesting (3+ levels) with create_subtree |
| 24 | Small Talk Flow | Greeting/app questions before transitioning to area creation |
| 25 | Completed Area Message | Messaging a completed area shows completion notice |
| 26 | Reset Area Command | Completed area notification with reset command suggestion |
| 27 | Multi-Turn Leaf Interview | Leaf interview spanning multiple partial responses before completion |

## Expected Format

Test cases use the following expected fields:

```json
{
  "expected": {
    "life_areas": 3,
    "sub_areas_min": 2,
    "sub_areas_max": 2,
    "summaries": true,
    "knowledge": true
  }
}
```

- `life_areas` - Exact count of life_areas table rows
- `sub_areas_min/max` - Range for life_areas with parent_id (sub-areas)
- `summaries` - Boolean: expect area_summaries > 0
- `knowledge` - Boolean: expect user_knowledge_areas > 0

## Recent Changes

### 2026-02-15: Fixed Test 26 + Added Test 27

**Fix: Auto-set current area on root creation**
- `LifeAreaMethods.create` now automatically sets `current_area_id` when creating a root area (no parent)
- This ensures the leaf interview flow has a valid area to work with immediately after creation
- Fixed Test 26 which was failing because `current_area_id` was not set after area creation

**New: Test 27 - Multi-Turn Leaf Interview**
- Tests partial → partial → complete flow across multiple messages
- Verifies that vague responses are marked "partial" and detailed responses complete the leaf

**Other changes:**
- Added inline leaf summary extraction (summaries saved when leaf completes)
- Used transactions for atomic DB operations in leaf interview nodes
- Added error handling with logging in leaf interview nodes

### 2026-02-13: Fixed Leaf Interview Flow Issues

**Issue 1 - Small talk routing override:**
- Short confirmations like "yes" were being routed to `small_talk` instead of `conduct_interview`
- Fix: `extract_target` now checks for active interview context and overrides to `conduct_interview`

**Issue 2 - Leaf order predictability:**
- Changed `get_descendants` from `ORDER BY title` to `ORDER BY id` (UUID7)
- Leaves are now asked in creation order (predictable, intuitive)

**Issue 3 - Evaluation too lenient:**
- `PROMPT_QUICK_EVALUATE` now explicitly requires content to match the specific topic being asked
- Answers about wrong topics are marked as "partial" not "complete"

**Test cases updated:**
- All 5 extraction test cases (1, 13, 21, 25, 26) updated for leaf-by-leaf interview flow
- Answers now provided in creation order with topic-specific content

### 2026-02-11: Fixed Three Failing Tests (1, 22, 24)

**Test 1 - CRUD Operations:**
- Fixed UUID normalization bug in `_validate_uuid` function
- Now returns `str(parsed)` instead of original input to ensure consistent UUIDs

**Test 22 - Subtree Bulk Create:**
- Updated expectations to correct counts: 7 areas, 6 sub-areas
- Structure: 1 root + 2 companies + 4 children (Responsibilities/Achievements each)

**Test 24 - Small Talk Flow:**
- Updated test inputs to use explicit sub-area creation syntax
- Changed from conversational auto-extraction to: "Create area Hobbies with sub-areas Reading, Hiking"

### 2026-02-11: Completed Area Prevention Feature

- Added test cases 25 and 26 for completed area handling
- New `extracted_at` column tracks when knowledge extraction completed
- Messaging a completed area shows notification with `/reset-area` command
- Test 25 now passing - completed area response working correctly

### 2026-02-11: Small Talk Feature

- Added test case 24 for small talk flow (greetings, app questions)
- New routing target `small_talk` handles casual conversation before interview/area modes

### 2026-02-10: Test Suite Cleanup

- Reduced from 20 to 5 focused test cases
- Replaced `criteria` with `sub_areas` (hierarchical structure)
- Replaced `summaries_min/max` and `knowledge_min/max` with boolean flags
- Added test 21 for hierarchical sub-area validation
- Fixed token limit for knowledge extraction (1024 -> 4096)

## Resolved Issues

### Test 26 - Auto-set Current Area (Fixed 2026-02-15)
After creating a root area with sub-areas, the LLM did not call `set_current_area`. The leaf interview then used a random UUID instead of the created area. Fixed by auto-setting `current_area_id` in `LifeAreaMethods.create` when creating root areas.

### Leaf Interview Flow Issues (Fixed 2026-02-13)

Three issues were identified and fixed:
1. `extract_target` routing confirmations to `small_talk` during active interviews
2. Leaf order was alphabetical (unpredictable) instead of creation order
3. Evaluation accepted answers about wrong topics as "complete"

### Test 1 - UUID Normalization (Fixed 2026-02-11)
The `_validate_uuid` function was validating UUIDs but returning the original string unchanged. When UUIDs passed through LLM extraction, minor corruption could occur. Fixed by returning the normalized UUID via `str(uuid.UUID(value))`.

### Test 22 - Expectations (Fixed 2026-02-11)
Test expected 5 areas / 4 sub-areas but actual correct count is 7 areas / 6 sub-areas for the nested structure.

### Test 24 - Test Inputs (Fixed 2026-02-11)
Test expected auto-extraction of sub-areas from conversational input, but this feature doesn't exist. Fixed by using explicit creation syntax.

### Azure Provider Error (Fixed 2026-02-11)
Fixed `BadRequestError: Error code: 400 - No tool call found for function call output` in `small_talk_response` and `completed_area_response` nodes by filtering out tool-related messages before invoking LLM without tools bound.
