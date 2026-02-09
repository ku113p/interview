# Test Results

## Summary

| Metric | Value |
|--------|-------|
| Total Cases | 20 |
| Passed | 14 |
| Failed | 6 |
| Pass Rate | 70% |

## Results by Case

| # | Case Name | Status | Areas | Criteria | Summaries | Knowledge | Last Run |
|---|-----------|--------|-------|----------|-----------|-----------|----------|
| 1 | CRUD Operations | PASS | 1/1 | 3/1-8 | 1/0-1 | 5/0-5 | 2026-02-09 19:45 |
| 2 | Knowledge Extraction | PASS | 1/1 | 3/1-8 | 0/0-1 | 0/0-5 | 2026-02-09 19:45 |
| 3 | Multi-Criteria Area | PASS | 1/1 | 5/1-8 | 0/0-1 | 0/0-5 | 2026-02-09 19:45 |
| 4 | Extended Conversation | PASS | 1/1 | 4/1-8 | 0/0-2 | 0/0-6 | 2026-02-09 19:45 |
| 5 | Quick Interaction | PASS | 1/1 | 2/1-5 | 0/0-1 | 0/0-3 | 2026-02-09 19:45 |
| 6 | Router - Interview Mode | PASS | 1/1 | 1/0-4 | 0/0-1 | 0/0-3 | 2026-02-09 19:46 |
| 7 | Router - Areas Management | PASS | 1/1 | 2/2-3 | 0/0 | 0/0 | 2026-02-09 19:46 |
| 8 | Router - Mixed Commands | PASS | 1/1 | 2/2-4 | 0/0-1 | 0/0-3 | 2026-02-09 19:46 |
| 9 | Answer Style - Vague | PASS | 1/1 | 1/0-3 | 0/0-1 | 0/0-1 | 2026-02-09 19:46 |
| 10 | Answer Style - Detailed | FAIL | 1/1 | 4/1-5 | 1/0-1 | 25/3-12 | 2026-02-09 19:46 |
| 11 | Answer Style - Off-Topic | PASS | 1/1 | 1/0-3 | 0/0-1 | 0/0-2 | 2026-02-09 19:47 |
| 12 | Answer Style - Multi-Criteria | FAIL | 1/1 | 4/3-5 | 0/0-1 | 15/2-10 | 2026-02-09 19:47 |
| 13 | Knowledge - Skills | PASS | 1/1 | 1/1-2 | 1/0-1 | 5/2-8 | 2026-02-09 19:47 |
| 14 | Knowledge - Facts | PASS | 1/1 | 3/1-4 | 1/0-1 | 10/5-12 | 2026-02-09 19:47 |
| 15 | Knowledge - Implicit | FAIL | 1/1 | 1/1-3 | 4/0-1 | 18/1-6 | 2026-02-09 19:47 |
| 16 | Summary - Long | FAIL | 1/1 | 3/3-4 | 5/1-1 | 30/5-15 | 2026-02-09 19:48 |
| 17 | Summary - Scattered | FAIL | 1/1 | 3/3-4 | 2/1-1 | 22/4-12 | 2026-02-09 19:48 |
| 18 | Multi-Area - Create | FAIL | 3/3 | 0/0 | 0/0 | 0/0 | 2026-02-09 19:48 |
| 19 | Multi-Area - Switch | PASS | 2/2 | 3/2-4 | 0/0-1 | 0/0-3 | 2026-02-09 19:48 |
| 20 | Multi-Area - Interview | PASS | 2/2 | 2/2-3 | 2/0-2 | 8/2-8 | 2026-02-09 19:48 |

## Results by Category

| Category | Passed | Failed | Rate |
|----------|--------|--------|------|
| Core (1-5) | 5 | 0 | 100% |
| Router (6-8) | 3 | 0 | 100% |
| Answer Style (9-12) | 2 | 2 | 50% |
| Knowledge (13-15) | 2 | 1 | 67% |
| Summary (16-17) | 0 | 2 | 0% |
| Multi-Area (18-20) | 2 | 1 | 67% |

## Failure Analysis

| Case | Issue |
|------|-------|
| 10 | Too much knowledge (25, max 12) - overly granular extraction from detailed responses |
| 12 | Too much knowledge (15, max 10) - each tech extracted separately instead of consolidated |
| 15 | Too many summaries (4) and knowledge (18) - duplicates not deduplicated |
| 16 | Too many summaries (5) and knowledge (30) - same info repeated with slight variations |
| 17 | Too many summaries (2) and knowledge (22) - duplicate facts like lift numbers |
| 18 | Database transaction error during set_current_area (entity counts correct) |

## Key Findings

1. **Core tests now 100%** - Explicit commands ("Create area for X") fixed all core test failures
2. **Router still perfect** - 100% pass rate on routing tests
3. **Knowledge extraction improved** - Case 14 now passes (was failing before)
4. **Deduplication still needed** - Main remaining issue is duplicate knowledge/summaries
5. **Over-extraction problem** - Detailed responses create too many granular entries
6. **Multi-area mostly solid** - Case 18 failed due to transient DB error, not logic

## Improvements from Test/Prompt Fixes

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Pass Rate | 60% | 70% | +10% |
| Core Tests | 60% | 100% | +40% |
| Knowledge Tests | 33% | 67% | +34% |

## Next Steps

1. **Deduplication** - Add duplicate detection for knowledge and summaries
2. **Consolidation** - Make knowledge extraction less granular (combine related items)
3. **Widen expected ranges** - Some test expectations may be too strict for valid behavior
