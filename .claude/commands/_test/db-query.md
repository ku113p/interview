# DB Query

Execute SQLite query against interview.db.

## Arguments
$ARGUMENTS: SQL query string

## Instructions

Query test database (default for skills):
```bash
sqlite3 -header -column test-interview.db "$ARGUMENTS"
```

Query production database:
```bash
sqlite3 -header -column interview.db "$ARGUMENTS"
```

## Quick Examples

**Find recent test users:**
```bash
/_test:db-query "SELECT DISTINCT user_id FROM life_areas ORDER BY created_at DESC LIMIT 5"
```

**Query specific test user's data:**
```bash
# Replace with actual UUID from above
/_test:db-query "SELECT * FROM life_areas WHERE user_id = 'cc546fc0-2dc6-4ffa-bdd4-e791e91f1ef4'"
```

**Count all test data:**
```bash
/_test:db-query "SELECT COUNT(DISTINCT user_id) as users, COUNT(*) as total_areas FROM life_areas"
```

## Common Queries

**Count all entities for a user:**
```sql
SELECT
  (SELECT COUNT(*) FROM life_areas WHERE user_id = 'UUID') as areas,
  (SELECT COUNT(*) FROM life_areas WHERE user_id = 'UUID' AND parent_id IS NOT NULL) as sub_areas,
  (SELECT COUNT(*) FROM summaries JOIN life_areas ON summaries.area_id = life_areas.id WHERE life_areas.user_id = 'UUID') as summaries,
  (SELECT COUNT(DISTINCT uk.id) FROM user_knowledge uk JOIN summaries s ON uk.summary_id = s.id JOIN life_areas la ON s.area_id = la.id WHERE la.user_id = 'UUID') as knowledge,
  (SELECT COUNT(*) FROM histories WHERE user_id = 'UUID') as history
```

**List life areas:**
```sql
SELECT id, title FROM life_areas WHERE user_id = 'UUID'
```

**List sub-areas for area (direct children):**
```sql
SELECT id, title FROM life_areas WHERE parent_id = 'AREA_UUID'
```

**List all descendants of an area:**
```sql
WITH RECURSIVE descendants AS (
  SELECT id, title, parent_id, 0 as depth FROM life_areas WHERE id = 'AREA_UUID'
  UNION ALL
  SELECT la.id, la.title, la.parent_id, d.depth + 1
  FROM life_areas la JOIN descendants d ON la.parent_id = d.id
)
SELECT id, title, depth FROM descendants WHERE depth > 0 ORDER BY depth, title
```

**List summaries for a user:**
```sql
SELECT s.id, la.title, substr(s.summary_text, 1, 60) as summary_preview
FROM summaries s JOIN life_areas la ON s.area_id = la.id WHERE la.user_id = 'UUID' ORDER BY s.created_at
```

**List knowledge for a user:**
```sql
SELECT uk.id, uk.description, uk.kind FROM user_knowledge uk
JOIN summaries s ON uk.summary_id = s.id
JOIN life_areas la ON s.area_id = la.id WHERE la.user_id = 'UUID'
```

**List history entries:**
```sql
SELECT id, input, response, created_at FROM histories WHERE user_id = 'UUID' ORDER BY created_at
```

**Count all users:**
```sql
SELECT COUNT(*) FROM users
```

**Recent test users (by UUID pattern):**
```sql
SELECT id, created_at FROM users ORDER BY created_at DESC LIMIT 10
```

## Notes

- Use single quotes for string values
- Test database: `test-interview.db` in project root (default for `/_test:*` skills)
- Production database: `interview.db` in project root
- Results displayed with headers and columns
- To query production DB, explicitly use: `sqlite3 -header -column interview.db "..."`
