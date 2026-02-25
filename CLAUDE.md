# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Monorepo containing an interactive interview assistant backend and a frontend landing page. The backend collects structured information through natural conversation, accepts text/audio/video input, maintains conversation history, asks follow-up questions based on sub-areas, and manages "life areas" (topics) to organize conversations.

## Commands

### Backend

All backend commands run from the `backend/` directory:

```bash
# Install dependencies
cd backend && make install

# Run CLI interface
cd backend && make run-cli
cd backend && make run-cli -- --user-id <uuid>  # Resume specific user session

# Testing
cd backend && make test                          # Run all tests
cd backend && make test-cov                      # Run tests with coverage
cd backend && uv run pytest tests/path/test.py -v  # Run single test file

# Code quality (runs via pre-commit hooks)
cd backend && uv run ruff check .                # Lint
cd backend && uv run ruff format .               # Format
```

**Required:** Set `OPENROUTER_API_KEY` environment variable before running.

### Frontend

All frontend commands run from the `frontend/` directory:

```bash
# Install dependencies
cd frontend && pnpm install

# Development server (localhost:4321)
cd frontend && pnpm dev

# Build static site
cd frontend && pnpm build

# Preview production build
cd frontend && pnpm preview

# Type checking
cd frontend && pnpm check

# Format code
cd frontend && pnpm format
cd frontend && pnpm format:check
```

## Architecture

See `backend/ARCHITECTURE.md` for detailed documentation of:
- Layer structure and dependencies
- Main workflow and subgraphs
- Worker pool architecture
- Database schema
- State models and patterns

### Key Files
- `backend/ARCHITECTURE.md` - Full architecture documentation
- `backend/src/processes/interview/graph.py` - Main LangGraph workflow
- `backend/src/processes/interview/state.py` - Central state model
- `backend/src/config/settings.py` - Model assignments, token limits
- `backend/src/infrastructure/db/managers.py` - Database access layer (async)

## Project Rules

### Git Commits
- Do not add Co-Authored-By lines to commit messages

### Pull Requests
- Do not add Claude as co-author or mention Claude in PR descriptions

### Python
- Use `uv run` for all Python commands (e.g., `uv run python`, `uv run pytest`)
- Run all `uv` commands from the `backend/` directory

### Linter Configuration
- Do not modify linter settings in `pyproject.toml` (ruff rules, max-statements, etc.)
- Do not use `# noqa` comments - refactor code to fix violations instead
- Do not use `# type: ignore` comments - fix the type issue properly instead

### Architecture Documentation
- When making structural changes (new modules, workflow changes, new subgraphs, database schema changes), update `backend/ARCHITECTURE.md` to reflect the changes
- Keep the architecture document in sync with the actual codebase

### LLM Configuration Documentation
- When making changes to AI/LLM logic (prompts, temperature, models, token limits, retry behavior), update `backend/LLM_MANIFEST.md` to reflect the changes
- Keep the LLM manifest in sync with actual AI behavior in the codebase

### Model Selection
- Do not use Google Gemini models for structured output (JSON responses)
- Gemini "thinking mode" generates excessive tokens for structured output
- Exception: Gemini is preferred for audio transcription (40x cheaper, plain text output)
- Use OpenAI GPT 5.x models for structured output (gpt-5.1-codex-mini, gpt-5.2, etc.)
