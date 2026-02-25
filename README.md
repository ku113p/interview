# Interview

Monorepo for the Interview assistant project.

## Structure

- **[backend/](backend/README.md)** — Python backend: conversational interview engine, LangGraph workflows, SQLite storage, MCP server
- **[frontend/](frontend/README.md)** — Landing page for demand validation (coming soon)
- **[business-plan/](business-plan/)** — Market research, monetization strategy, and validation plans

## Quick Start

```bash
cd backend
make install
export OPENROUTER_API_KEY=...
make run-cli
```

See [backend/README.md](backend/README.md) for full setup and usage instructions.
