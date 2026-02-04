# Interview

An interactive interview assistant that helps you collect structured information through a natural conversation. It accepts text, audio, or video input, remembers context, and asks the next most useful question so nothing important is missed. The system can run a guided interview against a set of criteria and can also manage "life areas" (topics) to keep the conversation organized.

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
- `make dev-setup` installs dev deps and registers Jupyter kernel
- `make jupyter` starts Jupyter Lab
- `make graph-check` validates graph visualization deps
- `make clean` removes `.venv`, cache, and `__pycache__`

Configuration
- `OPENROUTER_API_KEY` is required
- `INTERVIEW_DB_PATH` (optional) sets the SQLite file path; default is `interview.db`
