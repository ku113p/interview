# Test Infrastructure

Automated testing for the interview assistant using Claude Code skills.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Run All Tests | `/_test:run-all` | Run all test cases in parallel |
| DB Query | `/_test:db-query <sql>` | Execute SQL query against interview.db |
| View Results | `/_test:results` | Show current test results table |

## Running Tests

```bash
# Run all tests
/_test:run-all

# View results
/_test:results

# Query database directly
/_test:db-query "SELECT COUNT(*) FROM life_areas"

# Run single test via script
./scripts/test_report.sh .claude/commands/_test/cases/1-crud.json
```

## Test Cases

Located in `cases/`. Each JSON file defines:
- `name` - Test case name displayed in results
- `description` - What the test validates
- `inputs` - Simulated user messages sent to the assistant
- `expected` - Entity count expectations

### Current Cases

| # | Name | Focus |
|---|------|-------|
| 1 | CRUD Operations | Basic area + sub-area creation with interview |
| 5 | Quick Interaction | Minimal conversation, no extraction |
| 13 | Knowledge - Skill Extraction | Technical skill extraction |
| 18 | Multi-Area - Creation | Multiple root areas in one session |
| 21 | Tree Sub-Areas Full Flow | Hierarchical nested sub-areas |

## Expected Format

```json
{
  "name": "Test Name",
  "description": "What this tests",
  "inputs": ["user message 1", "user message 2", "/exit"],
  "expected": {
    "life_areas": 3,
    "sub_areas_min": 2,
    "sub_areas_max": 2,
    "summaries": true,
    "knowledge": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `life_areas` | int | Exact count of life_areas rows |
| `sub_areas_min/max` | int | Range for life_areas with parent_id |
| `summaries` | bool | Expect leaf_coverage with summary_text > 0 |
| `knowledge` | bool | Expect user_knowledge rows (via summary_id) > 0 |

## Adding Tests

1. Create `cases/<number>-<name>.json`
2. Define inputs and expected entity counts
3. Run `/_test:run-all` to execute

## Results

Results are stored in `results.md` with:
- Summary (total/passed/failed/rate)
- Per-case results with entity counts
- Test case descriptions
