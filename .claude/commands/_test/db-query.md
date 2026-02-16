# DB Query

Execute SQLite query against interview.db.

## Arguments
$ARGUMENTS: SQL query string

## Instructions

```bash
sqlite3 -header -column interview.db "$ARGUMENTS"
```

## Common Queries

**Count all entities for a user:**
```sql
SELECT
  (SELECT COUNT(*) FROM life_areas WHERE user_id = 'UUID') as areas,
  (SELECT COUNT(*) FROM life_areas WHERE user_id = 'UUID' AND parent_id IS NOT NULL) as sub_areas,
  (SELECT COUNT(*) FROM leaf_coverage WHERE root_area_id IN (SELECT id FROM life_areas WHERE user_id = 'UUID') AND summary_text IS NOT NULL) as summaries,
  (SELECT COUNT(*) FROM user_knowledge_areas WHERE user_id = 'UUID') as knowledge,
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
- Database: `interview.db` in project root
- Results displayed with headers and columns
