# Run All Tests

Run all test cases in `.claude/commands/_test/cases/` with parallel agents.

## Instructions

1. **Discover test cases:**
   - List all JSON files in `.claude/commands/_test/cases/`
   - Sort by filename (numeric order: 1-xxx, 5-xxx, 13-xxx, etc.)

2. **Run all in parallel:**
   - Launch Task agents in parallel using subagent_type=test-reporter
   - Each agent runs: `./scripts/test_report.sh .claude/commands/_test/cases/<file>.json`

3. **Collect results from each agent:**
   - Case number and name
   - PASS/FAIL status
   - Entity counts: areas, sub-areas, summaries, knowledge
   - Current timestamp for "Last Run"

4. **Update `.claude/commands/_test/results.md`:**
   - Update Summary table (Total, Passed, Failed, Pass Rate)
   - Update Results table with actual/expected values
   - Add timestamp to Last Run column

## Results Table Format

Use this exact format for the results table:

```markdown
| # | Case Name | Status | Areas | Sub-Areas | Summaries | Knowledge | Last Run |
|---|-----------|--------|-------|-----------|-----------|-----------|----------|
| 1 | CRUD Operations | PASS | 3/3 | 2/2-2 | 2/true | 8/true | 2026-02-10 21:58 |
```

Column format:
- **Areas**: `actual/expected` (e.g., `3/3`)
- **Sub-Areas**: `actual/min-max` (e.g., `2/2-2`)
- **Summaries**: `actual/expected` where expected is boolean (e.g., `2/true`)
- **Knowledge**: `actual/expected` where expected is boolean (e.g., `8/true`)
- **Last Run**: `YYYY-MM-DD HH:MM`

## Example Agent Prompt

For each test case, use subagent_type=test-reporter:
```
Run the test case and return the result:
./scripts/test_report.sh .claude/commands/_test/cases/<filename>.json

Extract and return: case name, PASS/FAIL status, and entity counts (areas, sub-areas, summaries, knowledge)
```
