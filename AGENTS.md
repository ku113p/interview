# AGENTS.md
# Guidance for agentic coding tools in this repo.

Project snapshot
- Language: Python (requires >=3.12 per pyproject.toml)
- Package layout: `src/` (import from `src.*` or relative modules)
- Entry point: `main.py`
- Domain: LangChain/LangGraph-based flows for interview routing

Build / Run / Lint / Test
Build
- No build system is configured.

Run
- Run the sample entry point via uv:
  - `uv run python main.py`

Lint
- No linting tool is configured (no ruff/flake8/black/isort config found).

Test
- No test framework or test commands are configured.
- There are no test files in the repository.
- When running python-based tests, use uv:
  - `uv run python -m pytest`

Single-test guidance
- Not applicable: no test framework or per-test runner is set up.

Code style guidelines

General principles
- Code must be understandable and readable at first pass.
- Methods/functions must be 15 total lines or fewer (including blanks/docstrings).
- Do not add code comments or docstrings; prefer clear names and structure.

Imports
- Prefer standard library imports first, then third-party, then local modules.
- Use explicit imports instead of wildcard imports.
- Local imports are either relative (e.g., `.methods`) or absolute from `src`.

Formatting
- Keep functions small and focused; return dict fragments for state updates.
- Use blank lines between top-level declarations.
- Favor explicit intermediate variables for readability (see `state = ...`).
- Prefer early returns to reduce nesting.
- Keep conditional routing simple and explicit.

Typing and data models
- Use `TypedDict` for LangGraph state payloads.
- Use `dataclass` for simple value objects (see `src/domain/*`).
- Use `enum.Enum` for finite modes/targets (InputMode, MessageType, Target).
- Prefer precise return types (`tuple[str, bool]`, `list[BaseMessage]`).
- Use `typing_extensions` for `TypedDict` in this repo.
- Use `pydantic.BaseModel` only when structured LLM output is required.
- Use `uuid.uuid7()` for new IDs (matches existing usage).

Async patterns
- Async functions are used for LLM calls and IO operations.
- Keep async boundaries explicit (`async def`, `await`), return plain dicts.
- Avoid mixing sync and async logic in the same node.

Naming conventions
- Enums use lower_snake for values (e.g., `interview`, `areas`).
- Functions are snake_case and direct (`extract_text`, `route_message`).
- TypedDict classes are named `State` inside each module.
- Graph nodes use short, action-oriented names (`extract_text`, `tools`).

Error handling
- Raise explicit errors for unsupported cases (`NotImplementedError`, `ValueError`).
- Use `KeyError` when access is invalid for a given user.
- Convert and validate external input early (UUID parsing in tools).
- For external processes (ffmpeg), raise `RuntimeError` on non-zero exit.
- Do not swallow LLM or IO errors; let failures surface clearly.

LangChain / LangGraph usage
- State graphs built via `StateGraph` with `START`/`END` edges.
- Use `add_messages` for message accumulation in state.
- LLMs are instantiated with OpenRouter base and `OPENROUTER_API_KEY`.
- Tool calls are handled via bound tools and ToolMessage responses.
- Use `bind_tools` or `with_structured_output` for tool/structure paths.
- Keep graph compilation in `get_subgraph()` or similar factory functions.

Project structure
- `src/domain`: domain types (User, Message, etc.)
- `src/graphs`: LangGraph graph definitions and nodes
- `src/db.py`: in-memory storage models
- `main.py`: simple entry point
- `uv.lock`: dependency lockfile (no tooling commands configured)

Repository conventions
- Graphs expose a `get_subgraph()` function returning a compiled graph.
- State payloads are plain dict fragments merged by LangGraph.
- LLM models use OpenRouter base URL explicitly.
- Keep routing logic in dedicated router functions.

Environment expectations
- `OPENROUTER_API_KEY` is required for LLM calls.
- `ffmpeg` is required for audio extraction from video.

Cursor / Copilot rules
- No Cursor rules found (`.cursor/rules/` or `.cursorrules` absent).
- No Copilot instructions found (`.github/copilot-instructions.md` absent).

Notes for agents
- Do not invent lint/test commands; none are configured.
- Keep edits minimal and consistent with existing patterns.
- Prefer adding type hints if changing or adding functions.
- Start work by updating or adding tests before code changes when possible.
- Use `uv run` for any python invocations (scripts, pytest, tooling).
