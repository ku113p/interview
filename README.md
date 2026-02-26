# Interview

Interactive interview assistant project.

## Structure

- **[backend/](backend/README.md)** — Python backend: conversational interview engine, LangGraph workflows, SQLite storage, MCP server
- **[frontend/](frontend/README.md)** — Astro landing page for demand validation (Version A: CV/Career, Version B: MCP/Technical)
- **[business-plan/](business-plan/)** — Market research, monetization strategy, and validation plans

Infrastructure and deploy scripts: [ku113p/infra](https://github.com/ku113p/infra)

## Quick Start

```bash
cd backend
make install
export OPENROUTER_API_KEY=...
make run-cli
```

See [backend/README.md](backend/README.md) for full setup and usage instructions.
