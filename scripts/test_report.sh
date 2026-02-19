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
SUB_AREAS_MIN=$(jq -r '.expected.sub_areas_min' "$CASE_FILE")
SUB_AREAS_MAX=$(jq -r '.expected.sub_areas_max' "$CASE_FILE")
EXPECT_SUMMARIES=$(jq -r '.expected.summaries // false' "$CASE_FILE")
EXPECT_KNOWLEDGE=$(jq -r '.expected.knowledge // false' "$CASE_FILE")

# Use /exit_30 if test expects knowledge or summaries (wait for background tasks)
if [ "$EXPECT_KNOWLEDGE" = "true" ] || [ "$EXPECT_SUMMARIES" = "true" ]; then
    INPUTS="${INPUTS//\/exit//exit_30}"
fi

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
    # Tests using /exit_N will wait N seconds for background tasks
    LOGFILE="/tmp/test_log_$USER_ID.json"
    echo "$INPUTS" | timeout 180 uv run python main.py --user-id "$USER_ID" 2>"$LOGFILE" || true

    # Show all logs
    echo ""
    echo "Full logs:"
    cat "$LOGFILE" 2>/dev/null || echo "  (no logs)"

    # === SECTION 2: TEST RESULT ===
    echo ""
    echo ">>> TEST RESULT"
    echo ""

    # Query counts
    read AREAS SUB_AREAS SUMMARIES KNOWLEDGE <<< $(sqlite3 interview.db "
        SELECT
            (SELECT COUNT(*) FROM life_areas WHERE user_id = '$USER_ID'),
            (SELECT COUNT(*) FROM life_areas WHERE parent_id IS NOT NULL AND user_id = '$USER_ID'),
            (SELECT COUNT(*) FROM summaries JOIN life_areas ON summaries.area_id = life_areas.id WHERE life_areas.user_id = '$USER_ID'),
            (SELECT COUNT(DISTINCT uk.id) FROM user_knowledge uk JOIN summaries s ON uk.summary_id = s.id JOIN life_areas la ON s.area_id = la.id WHERE la.user_id = '$USER_ID')
    " | tr '|' ' ')

    # Determine status
    STATUS="PASS"
    ERRORS=""
    [ "$AREAS" -ne "$EXP_AREAS" ] && STATUS="FAIL" && ERRORS="areas=$AREAS(exp=$EXP_AREAS) "
    ([ "$SUB_AREAS" -lt "$SUB_AREAS_MIN" ] || [ "$SUB_AREAS" -gt "$SUB_AREAS_MAX" ]) && STATUS="FAIL" && ERRORS="${ERRORS}sub_areas=$SUB_AREAS(exp=$SUB_AREAS_MIN-$SUB_AREAS_MAX) "
    [ "$EXPECT_SUMMARIES" = "true" ] && [ "$SUMMARIES" -eq 0 ] && STATUS="FAIL" && ERRORS="${ERRORS}summaries=0(exp>0) "
    [ "$EXPECT_KNOWLEDGE" = "true" ] && [ "$KNOWLEDGE" -eq 0 ] && STATUS="FAIL" && ERRORS="${ERRORS}knowledge=0(exp>0) "

    # Check for errors in log (exclude httpx INFO lines that contain "Error" in HTTP status text)
    ERROR_LINES=$(grep -i "error\|exception\|traceback" "$LOGFILE" 2>/dev/null | grep -v '"name": "httpx"' || true)
    if [ -n "$ERROR_LINES" ]; then
        STATUS="FAIL"
        ERRORS="${ERRORS}log_errors "
        echo ""
        echo ">>> LOG ERRORS DETECTED"
        echo "$ERROR_LINES"
    fi

    [ "$STATUS" = "PASS" ] && TOTAL_PASSED=$((TOTAL_PASSED + 1)) || TOTAL_FAILED=$((TOTAL_FAILED + 1))

    echo "Status: $STATUS"
    [ -n "$ERRORS" ] && echo "Errors: $ERRORS"
    echo ""
    echo "Entity counts:"
    echo "  life_areas:  $AREAS (expected: $EXP_AREAS)"
    echo "  sub_areas:   $SUB_AREAS (expected: $SUB_AREAS_MIN-$SUB_AREAS_MAX)"
    echo "  summaries:   $SUMMARIES (expected: $EXPECT_SUMMARIES)"
    echo "  knowledge:   $KNOWLEDGE (expected: $EXPECT_KNOWLEDGE)"

    # === SECTION 3: SQL ENTITIES ===
    echo ""
    echo ">>> SQL ENTITIES"
    echo ""

    echo "Life Areas:"
    sqlite3 -header -column interview.db "SELECT id, title, parent_id FROM life_areas WHERE user_id = '$USER_ID'" 2>/dev/null || echo "  (none)"

    echo ""
    echo "Sub-Areas (life_areas with parent):"
    sqlite3 -header -column interview.db "SELECT id, title, parent_id FROM life_areas WHERE parent_id IS NOT NULL AND user_id = '$USER_ID'" 2>/dev/null || echo "  (none)"

    echo ""
    echo "Summaries:"
    sqlite3 -header -column interview.db "SELECT s.id, la.title, substr(s.summary_text, 1, 60) as summary_preview FROM summaries s JOIN life_areas la ON s.area_id = la.id WHERE la.user_id = '$USER_ID'" 2>/dev/null || echo "  (none)"

    echo ""
    echo "Knowledge:"
    sqlite3 -header -column interview.db "SELECT uk.id, uk.description, uk.kind FROM user_knowledge uk JOIN summaries s ON uk.summary_id = s.id JOIN life_areas la ON s.area_id = la.id WHERE la.user_id = '$USER_ID'" 2>/dev/null || echo "  (none)"

    # Keep log for inspection
    echo ""
    echo "Log file: $LOGFILE"
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
