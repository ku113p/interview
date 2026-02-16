---
name: review-plan
description: |
  Use this skill when the user asks to "review plan", "reinspect code",
  "return final plan", "validate plan", or wants to check the current plan.
  This skill reads the active plan file, inspects relevant code files,
  and provides a comprehensive plan review.
version: 1.0.0
tools: Read, Glob, Grep
---

# Review Plan

Reviews the current implementation plan by reading the plan file and validating it against the actual codebase.

## Workflow

1. **Locate Active Plan**
   - Check `~/.claude/plans/` for active plan file
   - Read the plan to understand the proposed changes

2. **Identify Critical Files**
   - Extract file paths mentioned in the plan
   - Note any functions, classes, or modules referenced

3. **Inspect Codebase**
   - Use Read tool for specific files mentioned in plan
   - Use Glob to find related files if patterns are mentioned
   - Use Grep to search for functions/classes if needed

4. **Validate Plan**
   - Check if referenced files exist at specified locations
   - Verify that proposed changes align with current code structure
   - Identify any discrepancies between plan assumptions and reality

5. **Generate Review Report**

## Output Format

Return a structured review:

```markdown
# Plan Review

## Plan Summary
[Brief description of what the plan proposes]

## Files Verified
- `path/to/file.py` - [status/notes]
- `path/to/other.py` - [status/notes]

## Validation Results
- ✓ [Item that checks out]
- ⚠ [Item that needs attention]
- ✗ [Item with issues]

## Discrepancies Found
[Any misalignments between plan and codebase]

## Recommendations
[Suggested adjustments to the plan]

## Conclusion
[Ready to proceed / Needs revision / Other action needed]
```
