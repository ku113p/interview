#!/bin/bash
# Test runner with complete output for subagent reporting
# Usage: ./scripts/test_report.sh <case_file> [--repeat N]
#
# Outputs everything needed for report:
#   1. Test execution logs
#   2. Final results (PASS/FAIL)
#   3. All SQL entities created

set -e
cd "$(dirname "$0")/.."

# Load environment
if [ -f .env ]; then
    source .env
    export OPENROUTER_API_KEY
fi

# Parse arguments
CASE_FILE="$1"
REPEAT=1
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --repeat) REPEAT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

if [ -z "$CASE_FILE" ] || [ ! -f "$CASE_FILE" ]; then
    echo "Usage: ./scripts/test_report.sh <case_file> [--repeat N]"
    exit 1
fi

# Parse case
CASE_NAME=$(jq -r '.name' "$CASE_FILE")
INPUTS=$(jq -r '.inputs | join("\n")' "$CASE_FILE")
EXP_AREAS=$(jq -r '.expected.life_areas' "$CASE_FILE")
CRIT_MIN=$(jq -r '.expected.criteria_min' "$CASE_FILE")
CRIT_MAX=$(jq -r '.expected.criteria_max' "$CASE_FILE")
SUM_MIN=$(jq -r '.expected.summaries_min' "$CASE_FILE")
SUM_MAX=$(jq -r '.expected.summaries_max' "$CASE_FILE")
KNOW_MIN=$(jq -r '.expected.knowledge_min' "$CASE_FILE")
KNOW_MAX=$(jq -r '.expected.knowledge_max' "$CASE_FILE")

echo "════════════════════════════════════════════════════════════════"
echo "TEST: $CASE_NAME"
echo "FILE: $CASE_FILE"
echo "RUNS: $REPEAT"
echo "════════════════════════════════════════════════════════════════"

TOTAL_PASSED=0
TOTAL_FAILED=0

for RUN in $(seq 1 $REPEAT); do
    USER_ID=$(uuidgen)

    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo "RUN $RUN | User: $USER_ID"
    echo "────────────────────────────────────────────────────────────────"

    # === SECTION 1: EXECUTION LOGS ===
    echo ""
    echo ">>> EXECUTION LOGS"
    echo ""

    # Run test, capture stderr (logs) to temp file, show stdout
    LOGFILE="/tmp/test_log_$USER_ID.json"
    echo "$INPUTS" | timeout 120 uv run python main.py --user-id "$USER_ID" 2>"$LOGFILE" || true
    sleep 3

    # Show key log events
    echo ""
    echo "Key events from logs:"
    cat "$LOGFILE" | jq -r 'select(.message) | "  [\(.timestamp // "?")] \(.message)"' 2>/dev/null | head -20 || echo "  (no logs)"

    # === SECTION 2: TEST RESULT ===
    echo ""
    echo ">>> TEST RESULT"
    echo ""

    # Query counts
    read AREAS CRITERIA SUMMARIES KNOWLEDGE <<< $(sqlite3 interview.db "
        SELECT
            (SELECT COUNT(*) FROM life_areas WHERE user_id = '$USER_ID'),
            (SELECT COUNT(*) FROM criteria WHERE area_id IN (SELECT id FROM life_areas WHERE user_id = '$USER_ID')),
            (SELECT COUNT(*) FROM area_summaries WHERE area_id IN (SELECT id FROM life_areas WHERE user_id = '$USER_ID')),
            (SELECT COUNT(*) FROM user_knowledge_areas WHERE user_id = '$USER_ID')
    " | tr '|' ' ')

    # Determine status
    STATUS="PASS"
    ERRORS=""
    [ "$AREAS" -ne "$EXP_AREAS" ] && STATUS="FAIL" && ERRORS="areas=$AREAS(exp=$EXP_AREAS) "
    ([ "$CRITERIA" -lt "$CRIT_MIN" ] || [ "$CRITERIA" -gt "$CRIT_MAX" ]) && STATUS="FAIL" && ERRORS="${ERRORS}criteria=$CRITERIA(exp=$CRIT_MIN-$CRIT_MAX) "
    ([ "$SUMMARIES" -lt "$SUM_MIN" ] || [ "$SUMMARIES" -gt "$SUM_MAX" ]) && STATUS="FAIL" && ERRORS="${ERRORS}summaries=$SUMMARIES(exp=$SUM_MIN-$SUM_MAX) "
    ([ "$KNOWLEDGE" -lt "$KNOW_MIN" ] || [ "$KNOWLEDGE" -gt "$KNOW_MAX" ]) && STATUS="FAIL" && ERRORS="${ERRORS}knowledge=$KNOWLEDGE(exp=$KNOW_MIN-$KNOW_MAX) "

    # Check for errors in log
    if grep -qi "error\|exception\|traceback" "$LOGFILE" 2>/dev/null; then
        STATUS="FAIL"
        ERRORS="${ERRORS}log_errors "
    fi

    [ "$STATUS" = "PASS" ] && TOTAL_PASSED=$((TOTAL_PASSED + 1)) || TOTAL_FAILED=$((TOTAL_FAILED + 1))

    echo "Status: $STATUS"
    [ -n "$ERRORS" ] && echo "Errors: $ERRORS"
    echo ""
    echo "Entity counts:"
    echo "  life_areas:  $AREAS (expected: $EXP_AREAS)"
    echo "  criteria:    $CRITERIA (expected: $CRIT_MIN-$CRIT_MAX)"
    echo "  summaries:   $SUMMARIES (expected: $SUM_MIN-$SUM_MAX)"
    echo "  knowledge:   $KNOWLEDGE (expected: $KNOW_MIN-$KNOW_MAX)"

    # === SECTION 3: SQL ENTITIES ===
    echo ""
    echo ">>> SQL ENTITIES"
    echo ""

    echo "Life Areas:"
    sqlite3 -header -column interview.db "SELECT id, title FROM life_areas WHERE user_id = '$USER_ID'" 2>/dev/null || echo "  (none)"

    echo ""
    echo "Criteria:"
    sqlite3 -header -column interview.db "SELECT c.id, c.title FROM criteria c JOIN life_areas a ON c.area_id = a.id WHERE a.user_id = '$USER_ID'" 2>/dev/null || echo "  (none)"

    echo ""
    echo "Summaries:"
    sqlite3 -header -column interview.db "SELECT s.id, substr(s.summary, 1, 60) as summary_preview FROM area_summaries s JOIN life_areas a ON s.area_id = a.id WHERE a.user_id = '$USER_ID'" 2>/dev/null || echo "  (none)"

    echo ""
    echo "Knowledge:"
    sqlite3 -header -column interview.db "SELECT id, area FROM user_knowledge_areas WHERE user_id = '$USER_ID'" 2>/dev/null || echo "  (none)"

    rm -f "$LOGFILE"
done

# === FINAL SUMMARY ===
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo "Total:  $REPEAT"
echo "Passed: $TOTAL_PASSED"
echo "Failed: $TOTAL_FAILED"
echo "Rate:   $((TOTAL_PASSED * 100 / REPEAT))%"
echo ""

[ "$TOTAL_FAILED" -eq 0 ]
