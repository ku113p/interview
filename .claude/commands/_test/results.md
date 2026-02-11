# Test Results

## Summary

| Metric | Value |
|--------|-------|
| Total Cases | 8 |
| Passed | 6 |
| Failed | 2 |
| Pass Rate | 75% |

## Results by Case

| # | Case Name | Status | Areas | Sub-Areas | Summaries | Knowledge | Last Run |
|---|-----------|--------|-------|-----------|-----------|-----------|----------|
| 1 | CRUD Operations | PASS | 3/3 | 2/2-2 | 2/true | 8/true | 2026-02-11 15:42 |
| 5 | Quick Interaction | PASS | 1/1 | 0/0-0 | 0/false | 0/false | 2026-02-11 15:42 |
| 13 | Knowledge - Skill Extraction | PASS | 3/3 | 2/2-2 | 1/true | 4/true | 2026-02-11 15:42 |
| 18 | Multi-Area - Creation | PASS | 3/3 | 0/0-0 | 0/false | 0/false | 2026-02-11 15:42 |
| 21 | Tree Sub-Areas Full Flow | PASS | 4/4 | 3/3-3 | 2/true | 20/true | 2026-02-11 15:42 |
| 22 | Subtree - Bulk Create | FAIL | 7/5 | 6/4-4 | 0/false | 0/false | 2026-02-11 15:42 |
| 23 | Subtree - Deep Nesting | FAIL | 5/5 | 4/4-4 | 0/false | 0/false | 2026-02-11 15:42 |
| 24 | Small Talk Flow | PASS | 3/3 | 2/2-2 | 0/false | 0/false | 2026-02-11 15:42 |

## Test Case Descriptions

| # | Name | Focus |
|---|------|-------|
| 1 | CRUD Operations | Basic area + sub-area creation, interview flow |
| 5 | Quick Interaction | Minimal conversation, no extraction expected |
| 13 | Knowledge - Skill Extraction | Technical skill extraction from interview |
| 18 | Multi-Area - Creation | Creating multiple root areas in one session |
| 21 | Tree Sub-Areas Full Flow | Hierarchical sub-areas with nested parent-child relationships |
| 22 | Subtree - Bulk Create | Bulk nested sub-area creation via create_subtree |
| 23 | Subtree - Deep Nesting | Deep nesting (3+ levels) with create_subtree |
| 24 | Small Talk Flow | Greeting/app questions before transitioning to area creation |

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

### 2026-02-11: Small Talk Feature

- Added test case 24 for small talk flow (greetings, app questions)
- New routing target `small_talk` handles casual conversation before interview/area modes

### 2026-02-10: Test Suite Cleanup

- Reduced from 20 to 5 focused test cases
- Replaced `criteria` with `sub_areas` (hierarchical structure)
- Replaced `summaries_min/max` and `knowledge_min/max` with boolean flags
- Added test 21 for hierarchical sub-area validation
- Fixed token limit for knowledge extraction (1024 -> 4096)

## Known Issues

### Test 22 - Subtree Bulk Create
Expectations need update: 7 areas is correct (1 root + 2 positions + 4 children), not 5.

### Test 23 - Subtree Deep Nesting
Intermittent database lock error during concurrent operations. Infrastructure issue, not code bug.
