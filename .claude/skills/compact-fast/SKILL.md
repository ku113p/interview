---
name: compact-fast
description: |
  Use this skill when the user asks for "compact fast", "quick summary",
  "fast compaction", "haiku compact", or requests a faster/cheaper conversation summary.
  Summarizes the current conversation using the haiku model for speed and cost efficiency.
version: 1.0.0
model: haiku
tools: Read
---

# Fast Compaction

Generates a quick, cost-effective summary of the current conversation using the haiku model.

## Workflow

1. **Load Conversation History**
   - Read the current session transcript
   - Identify key conversation turns

2. **Extract Key Information**
   - User requests and goals
   - Decisions made
   - Code changes implemented
   - Problems encountered
   - Solutions applied
   - Pending tasks

3. **Generate Summary**
   - Use haiku model for fast processing
   - Focus on actionable insights
   - Keep it concise but complete

## Output Format

Return a structured summary:

```markdown
# Conversation Summary

## Context
[What was the user trying to accomplish?]

## Key Decisions
- [Decision 1]
- [Decision 2]

## Changes Made
- `file/path.py` - [What was changed and why]
- `other/file.py` - [What was changed and why]

## Problems & Solutions
- **Problem**: [Issue encountered]
  **Solution**: [How it was resolved]

## Pending Tasks
- [ ] [Task 1]
- [ ] [Task 2]

## Important Context
[Any critical information to remember for next session]
```
