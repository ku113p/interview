# Run All Tests

Run all test cases in `.claude/commands/_test/cases/` with 5 parallel agents per batch.

## Instructions

1. **Discover test cases:**
   - List all JSON files in `.claude/commands/_test/cases/`
   - Sort by filename (numeric order: 1-xxx, 2-xxx, etc.)

2. **Run in batches of 5:**
   - Launch 5 Task agents in parallel using subagent_type=Bash
   - Each agent runs: `./scripts/test_report.sh .claude/commands/_test/cases/<file>.json`
   - Wait for all 5 to complete before starting next batch

3. **Collect results from each agent:**
   - Case name
   - PASS/FAIL status
   - Entity counts: areas, criteria, summaries, knowledge
   - Current timestamp for "Last Run"

4. **Update results table after each batch:**
   - Edit `.claude/commands/_test/results.md`
   - Update the row for each completed case
   - Update summary counts (Passed, Failed, Pass Rate)

5. **Final summary:**
   - Show pass rate and key findings
   - Note any patterns in failures

## Results Table Format

The results file at `.claude/commands/_test/results.md` should have:
- Summary section with total/passed/failed/rate
- Results table with columns: #, Case Name, Status, Areas, Criteria, Summaries, Knowledge, Last Run
- Category breakdown
- Failure analysis

## Example Agent Prompt

For each test case, use this prompt:
```
Run the test case and return the result:
./scripts/test_report.sh .claude/commands/_test/cases/<filename>.json

Extract and return: case name, PASS/FAIL status, and entity counts (areas, criteria, summaries, knowledge)
```
