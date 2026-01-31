# Refactor and Fix Plan

Decisions
- Tests: pytest.
- CLI: text-only input loop.
- DI: factory functions to build dependencies and inject into graph builders.

Plan
1. [x] Define a root State TypedDict that covers all graph needs.
2. [x] Add dependency factories and pass deps into graph builders.
3. [x] Implement tool call dispatcher in area methods.
4. [x] Replace incomplete src/graph.py with root graph composition.
5. [x] Normalize state keys and types across subgraphs.
6. [x] Align async/sync nodes under a single async graph.
7. [ ] Implement minimal CLI loop in main.py.
8. [~] Add pytest tests for nodes, subgraphs, and end-to-end.
9. [~] Run tests and validate CLI.

Notes
- Items marked [~] need explicit validation to confirm full coverage (state normalization, async alignment, CLI/tests).
- CLI loop work (item 7) has not started; scope and UX remain undefined.
