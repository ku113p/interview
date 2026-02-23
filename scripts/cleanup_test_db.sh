#!/bin/bash
# Clean up test database and all WAL/SHM/lock files
# Usage: ./scripts/cleanup_test_db.sh [--force]

set -e
cd "$(dirname "$0")/.."

DB_NAME="test-interview.db"
FORCE=false

if [ "$1" = "--force" ]; then
    FORCE=true
fi

if [ ! -f "$DB_NAME" ]; then
    echo "No test database found ($DB_NAME)"
    exit 0
fi

# Show statistics
USER_COUNT=$(sqlite3 "$DB_NAME" "SELECT COUNT(DISTINCT user_id) FROM life_areas" 2>/dev/null || echo "0")
AREA_COUNT=$(sqlite3 "$DB_NAME" "SELECT COUNT(*) FROM life_areas" 2>/dev/null || echo "0")
HISTORY_COUNT=$(sqlite3 "$DB_NAME" "SELECT COUNT(*) FROM histories" 2>/dev/null || echo "0")

echo "Test Database: $DB_NAME"
echo "  Users:     $USER_COUNT"
echo "  Areas:     $AREA_COUNT"
echo "  Histories: $HISTORY_COUNT"
echo ""

# Confirm unless --force
if [ "$FORCE" = false ]; then
    read -p "Delete test database and all related files? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Remove all database files (includes WAL, SHM, lock)
rm -f ${DB_NAME}*
echo "Deleted: ${DB_NAME}*"
echo "Test database cleaned up successfully."
