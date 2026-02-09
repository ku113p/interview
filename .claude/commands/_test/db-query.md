# DB Query

Execute SQLite query against interview.db.

## Arguments
$ARGUMENTS: SQL query string

## Instructions

```bash
cd /home/ubuntu/docs/python/interview
sqlite3 -header -column interview.db "$ARGUMENTS"
```

## Common Queries

**Count all entities for a user:**
```sql
SELECT
  (SELECT COUNT(*) FROM life_areas WHERE user_id = 'UUID') as areas,
  (SELECT COUNT(*) FROM criteria WHERE area_id IN (SELECT id FROM life_areas WHERE user_id = 'UUID')) as criteria,
  (SELECT COUNT(*) FROM area_summaries WHERE area_id IN (SELECT id FROM life_areas WHERE user_id = 'UUID')) as summaries,
  (SELECT COUNT(*) FROM user_knowledge_areas WHERE user_id = 'UUID') as knowledge,
  (SELECT COUNT(*) FROM histories WHERE user_id = 'UUID') as history
```

**List life areas:**
```sql
SELECT id, title FROM life_areas WHERE user_id = 'UUID'
```

**List criteria for area:**
```sql
SELECT id, title FROM criteria WHERE area_id = 'AREA_UUID'
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
