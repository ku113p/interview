---
name: test-reporter
description: Runs a test case and generates a report with logs, results, and SQL entities
tools: Bash, Read
model: haiku
---

# Test Reporter Agent

Run a test case and produce a report.

## Command

```bash
./scripts/test_report.sh <case_file> [--repeat N]
```

Cases are in `.claude/commands/_test/cases/`:
- `1-crud.json` - Basic CRUD operations
- `2-knowledge.json` - Knowledge extraction
- `3-multi-criteria.json` - Multiple criteria
- `4-extended.json` - Extended conversation
- `5-quick.json` - Quick interaction

## Script Output

The script outputs everything you need:
1. **Execution logs** - key events from the test run
2. **Test result** - PASS/FAIL with entity counts vs expected
3. **SQL entities** - all created life_areas, criteria, summaries, knowledge

## Your Task

Run the script, read its output, and produce a concise markdown report summarizing:
- Overall status (PASS/FAIL)
- Entity counts
- Notable log events
- Brief conclusion

Do NOT run any other commands - the script output has all data needed.
