# LLM Manifest

This document describes all AI/LLM behavior in the interview assistant codebase. Keep this in sync with actual code when making changes.

## Model Assignments

| Node | Model | Purpose |
|------|-------|---------|
| `extract_target` | `gpt-5.1-codex-mini` | Fast intent classification (interview vs areas) |
| `interview_analysis` | `gpt-5.1-codex-mini` | Sub-area coverage analysis |
| `interview_response` | `gpt-5.2` | User-facing conversational responses |
| `area_chat` | `gpt-5.1-codex-mini` | Hierarchical area management with tools |
| `transcribe` | `gemini-2.5-flash-lite` | Audio transcription |
| `knowledge_extraction` | `gpt-5.1-codex-mini` | Extract skills/facts from summaries |

**Configuration location:** `src/config/settings.py` (MODEL_* constants)

## Temperature Configuration

| Node | Temperature | Rationale |
|------|-------------|-----------|
| `extract_target` | 0.0 | Deterministic classification |
| `transcribe` | 0.0 | Deterministic transcription |
| `interview_analysis` | 0.2 | Low variance for structured analysis |
| `area_chat` | 0.2 | Consistent tool-calling behavior |
| `interview_response` | 0.5 | Natural conversational variation |

**Configuration location:** `src/config/settings.py` (TEMPERATURE_* constants)

## Token Limits

### Output Tokens (max_tokens)

| Category | Limit | Used By |
|----------|-------|---------|
| Structured output | 1024 | `extract_target` |
| Analysis | 4096 | `interview_analysis` (variable-size sub-area output) |
| Knowledge extraction | 4096 | `knowledge_extraction` (needs reasoning tokens) |
| Conversational | 4096 | `interview_response`, `area_chat` |
| Transcription | 8192 | `transcribe` |

### Input Token Budgets

| Node | Budget | Purpose |
|------|--------|---------|
| Interview response | 8000 | History context limit |

### Message History Limits

| Setting | Limit | Purpose |
|---------|-------|---------|
| `HISTORY_LIMIT_GLOBAL` | 15 | Default for most nodes |
| `HISTORY_LIMIT_EXTRACT_TARGET` | 5 | Limited context for classification |
| `HISTORY_LIMIT_INTERVIEW` | 8 | Interview response history |

**Configuration location:** `src/config/settings.py`

## Pre-configured LLM Instances

LLM instances are created via lazy-initialized getters in `src/infrastructure/llms.py`:

| Getter | Model | Temperature | Max Tokens | Notes |
|--------|-------|-------------|------------|-------|
| `get_llm_extract_target()` | gpt-5.1-codex-mini | 0.0 | 1024 | |
| `get_llm_transcribe()` | gemini-2.5-flash-lite | 0.0 | 8192 | |
| `get_llm_interview_analysis()` | gpt-5.1-codex-mini | 0.2 | 4096 | |
| `get_llm_area_chat()` | gpt-5.1-codex-mini | 0.2 | 4096 | |
| `get_llm_interview_response()` | gpt-5.2 | 0.5 | 4096 | |

These getters use `@lru_cache` to ensure each LLM is only instantiated once. Called by `src/application/graph.py` at graph build time.

### Worker Pool LLMs

The extract worker pool creates its own LLM instance in `src/application/workers/extract_worker.py`:

| Worker | Model | Max Tokens | Notes |
|--------|-------|------------|-------|
| `knowledge_extraction` | gpt-5.1-codex-mini | 4096 | Needs extra tokens for reasoning |

## Prompt Locations

All prompts are centralized in `src/shared/prompts.py`:

| Purpose | Constant/Function |
|---------|-------------------|
| Intent classification | `PROMPT_EXTRACT_TARGET_TEMPLATE`, `build_extract_target_prompt()` |
| Sub-area coverage analysis | `PROMPT_INTERVIEW_ANALYSIS` |
| Interview response | `PROMPT_INTERVIEW_RESPONSE_TEMPLATE`, `build_interview_response_prompt()` |
| Hierarchical area management | `PROMPT_AREA_CHAT_TEMPLATE`, `build_area_chat_prompt()` |
| Audio transcription | `PROMPT_TRANSCRIBE` |

Template functions are used when prompts require dynamic values (e.g., user ID, sub-area status).

### Area Chat Decomposition Behavior

The `area_chat` prompt includes guidance to recognize overly broad sub-areas and suggest decomposition. This ensures interview topics are specific enough for focused coverage.

**Broad topic signals:**
- Plural/general terms: "experiences", "skills", "projects", "jobs"
- Container concepts: "background", "history", "overview"
- Multi-entity topics: covers multiple companies, schools, or projects

**Decomposition patterns:**

| Broad Topic | Recommended Structure |
|-------------|----------------------|
| Work/Job Experience | Per position: Company - Role → Responsibilities, Achievements, Projects, Skills |
| Education | Per institution: University → Degree, Key Courses, Projects/Thesis, Activities |
| Projects | Per project: Project Name → Role, Technologies, Challenges, Outcomes |
| Skills | Per category: Technical/Languages → specific skills as sub-areas |

**Behavior:** After creating a broad topic, the LLM confirms creation and proactively suggests breaking it down with concrete examples, offering to create the sub-structure.

### Bulk Sub-Area Creation (`create_subtree` tool)

The `create_subtree` tool allows creating an entire hierarchy of sub-areas in one call. The LLM uses this when:
- User lists multiple items to create at once
- User accepts a decomposition suggestion
- Creating known patterns (e.g., positions with Responsibilities/Achievements/Projects)

**Input schema:**
```python
class SubAreaNode(BaseModel):
    title: str
    children: list[SubAreaNode] = []

class CreateSubtreeArgs(BaseModel):
    user_id: str
    parent_id: str  # Attach subtree under this area
    subtree: list[SubAreaNode]
```

**Example:** Creating two job positions with sub-topics:
```json
{
  "parent_id": "<work-experience-uuid>",
  "subtree": [
    {"title": "Google - Engineer", "children": [
      {"title": "Responsibilities"},
      {"title": "Achievements"}
    ]},
    {"title": "Amazon - SDE", "children": [
      {"title": "Projects"}
    ]}
  ]
}
```

### Interview Analysis Prompt Structure

The `interview_analysis` node receives sub-areas in two formats for LLM context:

1. **Tree text** (`sub_areas_tree`): Indented hierarchy for visual context
   ```
   Work
     Projects
     Skills
   Education
   ```

2. **Paths** (`sub_area_paths`): Unambiguous identifiers for structured output
   ```
   ["Work", "Work > Projects", "Work > Skills", "Education"]
   ```

This dual representation helps the LLM understand hierarchy while producing unambiguous coverage analysis. Paths disambiguate duplicate titles (e.g., "Skills" under "Work" vs "Skills" under "Hobbies").

### Knowledge Extraction Prompt Structure

The `extract_summaries` node in `knowledge_extraction` subgraph also uses the tree/paths format to summarize user responses per sub-area.

## Error Handling

### Retry Configuration

LLM API calls use exponential backoff retry:
- **Max attempts:** 3
- **Initial wait:** 1 second
- **Max wait:** 10 seconds
- **Multiplier:** 2
- **Retried errors:**
  - `ConnectionError` - Network connectivity issues
  - `TimeoutError` - Request timeouts
  - HTTP 429 - Rate limits
  - HTTP 500, 502, 503, 504 - Server errors

Non-retryable HTTP errors (400, 401, 403, 404, etc.) fail immediately.

**Implementation:** `src/shared/retry.py`

### Applied to:
- `extract_target.py` - Intent classification
- `interview_analysis.py` - Structured output call
- `interview_response.py` - Chat response
- `area_loop/nodes.py` - Area chat with tools
- `transcribe/extract_text.py` - Audio transcription

## Known Limitations

1. **Token counting is approximate:** Uses character-based estimation (4 chars per token) rather than model-specific tokenizers for performance.

2. **Message trimming is by token budget:** Long messages may be trimmed mid-content. Consider summarization for very long histories.

3. **No streaming:** All LLM calls are blocking. For long responses, users wait for full completion.

4. **Provider-dependent behavior:** OpenRouter may have different rate limits or behaviors than direct API access.

## LLMClientBuilder

The `LLMClientBuilder` dataclass (`src/infrastructure/ai.py`) standardizes LLM client creation:

```python
@dataclass
class LLMClientBuilder:
    model: str
    temperature: float | None = None
    max_tokens: int | None = None
```

All parameters are passed through to ChatOpenAI. Use explicit temperatures for consistency.
