# Interview

An interactive interview assistant that helps you collect structured information through a natural conversation. It accepts text, audio, or video input, remembers context, and asks the next most useful question so nothing important is missed. The system can run a guided interview through hierarchical sub-areas and can also manage "life areas" (topics) to keep the conversation organized.

Future use cases
- Requirements gathering for product or research interviews
- HR screening and onboarding with consistent coverage
- Coaching and self-reflection sessions with structured prompts
- Building a knowledge base for later search or RAG workflows

Requirements
- Python 3.12
- uv
- ffmpeg (for audio/video input)
- `OPENROUTER_API_KEY` (used via OpenRouter)

How to run
```bash
make install
export OPENROUTER_API_KEY=...  # required
make run-cli
```

Main make commands
- `make install` installs dependencies
- `make run-cli` starts the CLI (`make run-cli --user-id <uuid>` is supported)
- `make run-mcp` starts the MCP server (Streamable HTTP on port 8080)
- `make dev-setup` installs dev deps and registers Jupyter kernel
- `make jupyter` starts Jupyter Lab
- `make graph-check` validates graph visualization deps
- `make clean` removes `.venv`, cache, and `__pycache__`

Configuration
- `OPENROUTER_API_KEY` is required
- `INTERVIEW_DB_PATH` (optional) sets the SQLite file path; default is `interview.db`

MCP Server

The project exposes a read-only MCP server over Streamable HTTP. It provides tools to query areas, summaries, and extracted knowledge.

Starting the server
```bash
export OPENROUTER_API_KEY=...  # required for search_summaries
make run-mcp                   # listens on http://0.0.0.0:8080/mcp
```

Creating an API key

Send `/mcp_keys create <label>` in the chat (CLI or Telegram). The bot returns a raw key — save it, it won't be shown again. Use `/mcp_keys` to list keys and `/mcp_keys revoke <prefix>` to revoke.

Available tools
| Tool | Description |
|------|-------------|
| `get_areas` | List all life areas for the authenticated user |
| `get_summaries` | Get summaries, optionally filtered by area_id |
| `get_knowledge` | Get extracted skills/facts, optionally filtered by kind |
| `search_summaries` | Semantic search over summaries by query string |

Client configuration (Claude Desktop)

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "interview": {
      "type": "streamable-http",
      "url": "http://localhost:8080/mcp",
      "headers": {
        "Authorization": "Bearer <your-api-key>"
      }
    }
  }
}
```

Client configuration (Claude Code)

Add to `.mcp.json` in the project root or `~/.claude/mcp.json` globally:
```json
{
  "mcpServers": {
    "interview": {
      "type": "http",
      "url": "http://localhost:8080/mcp",
      "headers": {
        "Authorization": "Bearer <your-api-key>"
      }
    }
  }
}
```
