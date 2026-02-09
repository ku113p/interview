# Test Infrastructure

Automated testing for the interview assistant using Claude Code skills.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Run All Tests | `/_test:run-all` | Run all test cases in batches of 5 parallel agents |
| DB Query | `/_test:db-query <sql>` | Execute SQL query against interview.db |
| View Results | `/_test:results` | Show current test results table |

## Running Tests

```bash
# Run all tests
/_test:run-all

# View results
/_test:results

# Query database directly
/_test:db-query "SELECT COUNT(*) FROM users"
```

## Test Cases

Located in `cases/`. Each JSON file defines:
- `name` - Test case name displayed in results
- `description` - What the test validates
- `inputs` - Simulated user messages sent to the assistant
- `expected` - Entity count expectations (exact or min/max ranges)

## Categories

| Category | Cases | Tests |
|----------|-------|-------|
| Core | 1-5 | CRUD, knowledge, multi-criteria, extended, quick |
| Router | 6-8 | Interview mode, areas management, mixed commands |
| Answer Style | 9-12 | Vague, detailed, off-topic, multi-criteria responses |
| Knowledge | 13-15 | Skills, facts, implicit information extraction |
| Summary | 16-17 | Long conversations, scattered information |
| Multi-Area | 18-20 | Create, switch, cross-area interviews |

## Adding Tests

1. Create `cases/<number>-<name>.json`
2. Define inputs and expected entity counts
3. Run `/_test:run-all` to execute

## Results

Results are stored in `results.md` with:
- Summary (total/passed/failed/rate)
- Per-case results with entity counts
- Category breakdown
- Failure analysis
