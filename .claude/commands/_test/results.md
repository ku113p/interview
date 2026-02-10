# Test Results

## Summary

| Metric | Value |
|--------|-------|
| Total Cases | 5 |
| Passed | 4 |
| Failed | 1 |
| Pass Rate | 80% |

## Results by Case

| # | Case Name | Status | Areas | Sub-Areas | Summaries | Knowledge | Last Run |
|---|-----------|--------|-------|-----------|-----------|-----------|----------|
| 1 | CRUD Operations | PASS | 3/3 | 2/2-2 | 2/true | 6/true | 2026-02-10 22:34 |
| 5 | Quick Interaction | PASS | 1/1 | 0/0-0 | 0/false | 0/false | 2026-02-10 22:34 |
| 13 | Knowledge - Skill Extraction | PASS | 3/3 | 2/2-2 | 2/true | 7/true | 2026-02-10 22:34 |
| 18 | Multi-Area - Creation | PASS | 3/3 | 0/0-0 | 0/false | 0/false | 2026-02-10 22:34 |
| 21 | Tree Sub-Areas Full Flow | FAIL | 1/4 | 0/3-3 | 0/true | 0/true | 2026-02-10 22:34 |

## Test Case Descriptions

| # | Name | Focus |
|---|------|-------|
| 1 | CRUD Operations | Basic area + sub-area creation, interview flow |
| 5 | Quick Interaction | Minimal conversation, no extraction expected |
| 13 | Knowledge - Skill Extraction | Technical skill extraction from interview |
| 18 | Multi-Area - Creation | Creating multiple root areas in one session |
| 21 | Tree Sub-Areas Full Flow | Hierarchical sub-areas with nested parent-child relationships |

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

### 2026-02-10: Test Suite Cleanup

- Reduced from 20 to 5 focused test cases
- Replaced `criteria` with `sub_areas` (hierarchical structure)
- Replaced `summaries_min/max` and `knowledge_min/max` with boolean flags
- Added test 21 for hierarchical sub-area validation
- Fixed token limit for knowledge extraction (1024 -> 4096)
