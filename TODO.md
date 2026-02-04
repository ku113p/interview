## Completed
- [x] Document project purpose, setup, and limitations; replace placeholder description (README.md, pyproject.toml)
- [x] Make AI config robust: defer OPENROUTER_API_KEY lookup to runtime with clear errors (src/ai.py)
- [x] Fix tool binding so tools are actually available to the model (src/nodes/area_chat.py)
- [x] Align audio pipeline formats or transcode to known format (src/nodes/extract_audio.py, src/nodes/extract_text.py)
- [x] Add error handling around tool execution (src/nodes/area_tools.py)
- [x] Clarify loop behavior and increment logic for loop_step (src/routers/area_router.py, src/nodes/area_chat.py, src/nodes/area_tools.py)
- [x] Normalize or consolidate State models to avoid divergence (src/graph.py, src/routers/message_router.py)
- [x] Replace placeholder timestamps with real values (src/nodes/interview.py)
- [x] Clean up minor inconsistencies (duplicate imports, unused types) (src/routers/area_router.py)
- [x] Wire a minimal runnable entrypoint or note it's a stub (main.py)
- [x] Any tool call fail - need revert prev and stop continue and return success false
- [x] Timestamps for messages to save
- [x] Use only uuid7 as ids
- [x] SQLite

## High Priority Bugs & Issues
- [x] **CRITICAL**: Fix environment variable mismatch - .env has OPENROUTER_API_KEY but code expects OPENAI_API_KEY (src/ai.py:19)
- [ ] Fix message history ordering - currently loads newest first instead of oldest first (src/nodes/load_history.py:22-25)
- [ ] Fix potential race condition in MessageBuckets - multiple timestamps using time.time() could collide (src/nodes/save_history.py:56, src/nodes/interview.py:70)
- [ ] Add default values or proper validation for media_file and audio_file in State (src/state.py:34,40)
- [ ] Add ffmpeg availability check before attempting extraction (src/subgraph/extract_flow/nodes/extract_audio.py:52)
- [ ] Create test suite - zero test coverage currently exists

## Medium Priority Improvements
- [ ] Add empty list check for tool_calls in area_loop flow router (src/subgraph/area_loop/flow.py:8)
- [ ] Review database connection handling - ensure all connections properly closed (src/db.py:42-44)
- [ ] Remove or implement area_threshold node - currently unreachable dead code (src/subgraph/area_loop/flow.py:7-10, nodes/area_threshold.py)
- [ ] Add input validation for user messages (length limits, sanitization) (src/cli/session.py:109)
- [ ] Add UUID format validation in tool methods before casting (src/subgraph/area_loop/tools.py:11-17)
- [ ] Add structured logging throughout the application for debugging
- [ ] Implement proper secrets management instead of plain text API keys

## Low Priority / Technical Debt
- [ ] Extract repeated content normalization logic to shared utility function (appears in 4+ files)
- [ ] Improve error messages to be more user-friendly in CLI (src/cli/session.py, main.py)
- [ ] Document magic numbers - add constants with explanations (src/subgraph/area_loop/flow.py:3-4)
- [ ] Add type checking with mypy or pyright to pyproject.toml
- [ ] Implement database migration system for future schema changes
- [ ] Add docstrings to all public functions and classes