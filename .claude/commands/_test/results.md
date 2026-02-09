# Test Results

## Summary

| Metric | Value |
|--------|-------|
| Total Cases | 20 |
| Passed | 13 |
| Failed | 7 |
| Pass Rate | 65% |

## Results by Case

| # | Case Name | Status | Areas | Criteria | Summaries | Knowledge | Last Run |
|---|-----------|--------|-------|----------|-----------|-----------|----------|
| 1 | CRUD Operations | PASS | 1/1 | 3/1-8 | 0/0-1 | 0/0-5 | 2026-02-09 17:45 |
| 2 | Knowledge Extraction | PASS | 1/1 | 6/1-8 | 0/0-1 | 0/0-5 | 2026-02-09 17:45 |
| 3 | Multi-Criteria Area | PASS | 1/1 | 3/1-8 | 0/0-1 | 0/0-5 | 2026-02-09 17:45 |
| 4 | Extended Conversation | PASS | 1/1 | 1/1-8 | 0/0-2 | 0/0-6 | 2026-02-09 17:45 |
| 5 | Quick Interaction | PASS | 1/1 | 1/1-5 | 0/0-1 | 0/0-3 | 2026-02-09 17:45 |
| 6 | Router - Interview Mode | PASS | 1/1 | 0/0-4 | 0/0-1 | 0/0-3 | 2026-02-09 17:46 |
| 7 | Router - Areas Management | PASS | 1/1 | 2/2-3 | 0/0 | 0/0 | 2026-02-09 17:46 |
| 8 | Router - Mixed Commands | PASS | 1/1 | 2/2-4 | 0/0-1 | 0/0-3 | 2026-02-09 17:46 |
| 9 | Answer Style - Vague | PASS | 1/1 | 0/0-3 | 0/0-1 | 0/0-1 | 2026-02-09 17:46 |
| 10 | Answer Style - Detailed | FAIL | 0/1 | 0/1-5 | 0/0-1 | 0/3-12 | 2026-02-09 17:46 |
| 11 | Answer Style - Off-Topic | PASS | 1/1 | 0/0-3 | 0/0-1 | 0/0-2 | 2026-02-09 17:47 |
| 12 | Answer Style - Multi-Criteria | FAIL | 1/1 | 4/3-5 | 0/0-1 | 0/2-10 | 2026-02-09 17:47 |
| 13 | Knowledge - Skills | FAIL | 1/1 | 8/1-4 | 0/0-1 | 0/5-15 | 2026-02-09 17:47 |
| 14 | Knowledge - Facts | FAIL | 1/1 | 0/1-4 | 0/0-1 | 0/5-12 | 2026-02-09 17:47 |
| 15 | Knowledge - Implicit | FAIL | 1/1 | 0/1-3 | 0/0-1 | 0/1-6 | 2026-02-09 17:47 |
| 16 | Summary - Long | FAIL | 1/1 | 3/3-4 | 0/1 | 0/5-15 | 2026-02-09 17:48 |
| 17 | Summary - Scattered | FAIL | 1/1 | 8/3-4 | 0/1 | 0/4-12 | 2026-02-09 17:48 |
| 18 | Multi-Area - Create | PASS | 3/3 | 0/0 | 0/0 | 0/0 | 2026-02-09 17:48 |
| 19 | Multi-Area - Switch | PASS | 2/2 | 3/2-4 | 0/0-1 | 0/0-3 | 2026-02-09 17:48 |
| 20 | Multi-Area - Interview | PASS | 2/2 | 2/2-3 | 2/0-2 | 8/2-8 | 2026-02-09 17:48 |

## Results by Category

| Category | Passed | Failed | Rate |
|----------|--------|--------|------|
| Core (1-5) | 5 | 0 | 100% |
| Router (6-8) | 3 | 0 | 100% |
| Answer Style (9-12) | 2 | 2 | 50% |
| Knowledge (13-15) | 0 | 3 | 0% |
| Summary (16-17) | 0 | 2 | 0% |
| Multi-Area (18-20) | 3 | 0 | 100% |

## Failure Analysis

| Case | Issue |
|------|-------|
| 10 | No entities created - assistant kept asking to confirm area creation |
| 12 | No knowledge extracted from detailed tech stack answer |
| 13 | Too many criteria (8), no knowledge extracted from skills info |
| 14 | No criteria/knowledge extracted from career facts |
| 15 | No criteria/knowledge for implicit mountain biking info |
| 16 | No summaries/knowledge from photography conversation |
| 17 | Too many criteria (8), no summaries/knowledge |

## Key Findings

1. **Core functionality solid** - CRUD, extended conversations, and quick interactions all pass
2. **Router works well** - correctly routes between areas and interview modes
3. **Multi-area management works** - can create, switch, and interview across areas
4. **Knowledge extraction failing** - system not extracting knowledge from user answers (0% in Knowledge category)
5. **Summarization not triggered** - summaries not being generated (0% in Summary category)
6. **Criteria creation inconsistent** - sometimes too many (case 13, 17), sometimes none (case 14, 15)
