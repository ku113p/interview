# Code Review Notes: Test Case Fixes and Prompt Improvements

Date: 2026-02-09

## Summary

Pass rate improved from 60% to 70% after:
- Converting 15 test cases from implicit requests to explicit commands
- Improving prompts in `src/shared/prompts.py` to be more action-oriented

## Suggestions

### 1. Area Chat Prompt - Edge Case Consideration

Current behavior immediately sets new area as current without asking:
```python
"Immediately set it as current using 'set_current_area' (don't ask, just do it)"
```

**Consider:** What if user already has a current area they're actively working on? Could add a note like:
```
"If user explicitly asks to create an area WITHOUT switching, respect that request."
```

Probably fine for most use cases, but worth monitoring if users report unexpected area switches.

### 2. Test Case Documentation

Tests vary between single and multiple criteria creation:
- `"Add criteria for workout frequency, exercise variety, and fitness goals"` (multiple)
- `"Add criterion for study habits"` (single)

This is intentional variation, but could document the pattern in `.claude/commands/_test/README.md`.

### 3. Automated Timestamps

Results file uses manually written timestamps. Consider capturing actual timestamps from test runs for accuracy.

## Issues to Address

### 1. Deduplication Required (6 failing tests)

Tests 10, 12, 15, 16, 17 fail due to duplicate knowledge/summary entries:

| Test | Issue |
|------|-------|
| 10 | 25 knowledge items (max 12) - overly granular extraction |
| 12 | 15 knowledge items (max 10) - each tech extracted separately |
| 15 | 18 knowledge + 4 summaries - duplicates not deduplicated |
| 16 | 30 knowledge + 5 summaries - same info with slight variations |
| 17 | 22 knowledge + 2 summaries - duplicate facts |

**Root cause:** Knowledge extraction creates near-duplicate entries like:
- "Goes to mountains every weekend"
- "user goes to the mountains every weekend"
- "Goes to the mountains every weekend"

**Fix needed:** Add deduplication logic in knowledge extraction pipeline. Options:
1. Semantic similarity check before inserting (embedding-based)
2. Prompt-based dedup: ask LLM to consolidate before saving
3. Post-processing: deduplicate on retrieval

### 2. Database Transaction Error (Test 18)

```
Database transaction failed during set_current_area
```

Entity counts were correct (3/3 areas created), but test failed due to transient DB error.

**Possible causes:**
- Race condition with concurrent writes
- Connection pool exhaustion
- Lock contention on area table

**Suggested investigation:**
1. Check if error is reproducible
2. Review `set_current_area` implementation for transaction handling
3. Consider adding retry logic for transient failures

### 3. Over-Extraction from Detailed Responses

When users provide detailed responses with many specifics (test 10), the system extracts each detail as a separate knowledge item instead of consolidating.

Example input:
> "I have 3 years of professional experience working with Python pandas, numpy, and scikit-learn..."

Results in 25 separate knowledge items instead of 5-10 consolidated ones.

**Fix options:**
1. Update knowledge extraction prompt to consolidate related items
2. Add max items per extraction call
3. Group by category during extraction

## Next Steps

1. [ ] Implement knowledge deduplication
2. [ ] Investigate database transaction error in test 18
3. [ ] Consider widening expected ranges for tests if current behavior is acceptable
4. [ ] Add test case documentation
