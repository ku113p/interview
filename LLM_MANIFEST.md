# LLM Manifest

This document describes all AI/LLM behavior in the interview assistant codebase. Keep this in sync with actual code when making changes.

## Model Assignments

| Node | Model | Purpose |
|------|-------|---------|
| `extract_target` | `gpt-5.1-codex-mini` | Fast intent classification (interview vs areas vs small_talk) |
| `quick_evaluate` | `gpt-5.1-codex-mini` | Evaluate user answer for leaf (complete/partial/skipped) |
| `generate_leaf_response` | `gpt-5.1-codex-mini` | Generate focused questions about single leaf |
| `leaf_summary` | `gpt-5.1-codex-mini` | Extract summary when leaf completes |
| `small_talk_response` | `gpt-5.1-codex-mini` | Greetings, app questions, casual chat |
| `completed_area_response` | `gpt-5.1-codex-mini` | Response when area already extracted |
| `area_chat` | `gpt-5.1-codex-mini` | Hierarchical area management with tools |
| `transcribe` | `gemini-2.5-flash-lite` | Audio transcription |
| `knowledge_extraction` | `gpt-5.1-codex-mini` | Extract skills/facts from summaries |

**Configuration location:** `src/config/settings.py` (MODEL_* constants)

## Temperature Configuration

| Node | Temperature | Rationale |
|------|-------------|-----------|
| `extract_target` | 0.0 | Deterministic classification |
| `transcribe` | 0.0 | Deterministic transcription |
| `quick_evaluate` | 0.0 | Deterministic evaluation |
| `area_chat` | 0.2 | Consistent tool-calling behavior |
| `generate_leaf_response` | 0.5 | Natural conversational variation |
| `leaf_summary` | 0.5 | Natural variation in summary phrasing |
| `small_talk_response` | 0.5 | Natural conversational variation |
| `completed_area_response` | 0.5 | Natural conversational variation |

**Configuration location:** `src/config/settings.py` (TEMPERATURE_* constants)

## Token Limits

### Output Tokens (max_tokens)

| Category | Limit | Used By |
|----------|-------|---------|
| Structured output | 1024 | `extract_target` |
| Quick evaluate | 256 | `quick_evaluate` (status + reason only) |
| Leaf response | 1024 | `generate_leaf_response` (short focused questions) |
| Knowledge extraction | 4096 | `knowledge_extraction` (needs reasoning tokens) |
| Conversational | 4096 | `small_talk_response`, `completed_area_response`, `area_chat` |
| Transcription | 8192 | `transcribe` |

### Input Token Budgets

| Node | Budget | Purpose |
|------|--------|---------|
| Interview response | 8000 | History context limit |

### Message History Limits

| Setting | Limit | Purpose |
|---------|-------|---------|
| `HISTORY_LIMIT_GLOBAL` | 15 | Default for most nodes |
| `HISTORY_LIMIT_EXTRACT_TARGET` | 5 | Limited context for classification, small talk |
| `HISTORY_LIMIT_INTERVIEW` | 8 | Interview response history |

**Configuration location:** `src/config/settings.py`

## Pre-configured LLM Instances

LLM instances are created via lazy-initialized getters in `src/infrastructure/llms.py`:

| Getter | Model | Temperature | Max Tokens | Reasoning | Notes |
|--------|-------|-------------|------------|-----------|-------|
| `get_llm_extract_target()` | gpt-5.1-codex-mini | 0.0 | 1024 | low | Structured output |
| `get_llm_transcribe()` | gemini-2.5-flash-lite | 0.0 | 8192 | n/a | |
| `get_llm_quick_evaluate()` | gpt-5.1-codex-mini | 0.0 | 256 | low | Structured output |
| `get_llm_leaf_response()` | gpt-5.1-codex-mini | 0.5 | 1024 | default | |
| `get_llm_area_chat()` | gpt-5.1-codex-mini | 0.2 | 4096 | default | Tool-calling |
| `get_llm_small_talk()` | gpt-5.1-codex-mini | 0.5 | 4096 | default | |

These getters use `@lru_cache` to ensure each LLM is only instantiated once. Called by `src/processes/interview/graph.py` at graph build time.

### Worker Pool LLMs

The extract worker pool creates its own LLM instance in `src/processes/extract/worker.py`:

| Worker | Model | Max Tokens | Reasoning | Notes |
|--------|-------|------------|-----------|-------|
| `knowledge_extraction` | gpt-5.1-codex-mini | 4096 | low | Structured output |

Knowledge extraction is queued asynchronously when a leaf interview completes. The extract worker retrieves messages from `leaf_history` and extracts summaries and knowledge items.

## Prompt Locations

All prompts are centralized in `src/shared/prompts.py`:

| Purpose | Constant/Function |
|---------|-------------------|
| Intent classification | `PROMPT_EXTRACT_TARGET_TEMPLATE`, `build_extract_target_prompt()` |
| Quick evaluate (leaf answer) | `PROMPT_QUICK_EVALUATE` |
| Leaf question (initial) | `PROMPT_LEAF_QUESTION` |
| Leaf followup (partial) | `PROMPT_LEAF_FOLLOWUP` |
| Leaf transition (complete) | `PROMPT_LEAF_COMPLETE` |
| Leaf summary extraction | `PROMPT_LEAF_SUMMARY` |
| All leaves done | `PROMPT_ALL_LEAVES_DONE` |
| Small talk response | `PROMPT_SMALL_TALK` |
| Completed area response | `PROMPT_COMPLETED_AREA` (in completed_area_response.py) |
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

### Leaf Interview Prompts

The leaf interview flow uses focused prompts for each stage:

1. **Quick Evaluate** (`PROMPT_QUICK_EVALUATE`): Evaluates if user answered a single leaf topic
   - Input: leaf path, question asked, ALL accumulated messages
   - Output: status (complete/partial/skipped) + reason
   - ~300-500 tokens depending on accumulated messages

2. **Leaf Question** (`PROMPT_LEAF_QUESTION`): Generates initial question about one leaf
   - Input: leaf path (e.g., "Work > Google > Responsibilities")
   - Output: Single focused question
   - ~300 tokens

3. **Leaf Followup** (`PROMPT_LEAF_FOLLOWUP`): Asks for more detail after partial answer
   - Input: leaf path, accumulated messages, evaluation reason
   - Output: Acknowledgment + followup question
   - ~400 tokens

4. **Leaf Complete** (`PROMPT_LEAF_COMPLETE`): Transitions to next leaf
   - Input: completed leaf path, next leaf path
   - Output: Brief ack + question for next topic
   - ~300 tokens

5. **Leaf Summary** (`PROMPT_LEAF_SUMMARY`): Extracts summary when leaf is complete
   - Input: leaf path, accumulated conversation messages
   - Output: 2-4 sentence summary of user's responses for this topic
   - ~400 tokens
   - Summary is saved to `leaf_coverage.summary_text` with embedding vector

6. **All Leaves Done** (`PROMPT_ALL_LEAVES_DONE`): Completion message
   - Output: Thank you + suggestion for next steps
   - ~200 tokens

### Token Comparison (Old vs New)

| Scenario | Old (interview_analysis) | New (leaf flow) |
|----------|--------------------------|-----------------|
| Per turn | 8,000-26,000 | 700-1,200 |
| 20-turn interview | 500k+ cumulative | ~20k cumulative |

The new flow sends only the current leaf context, not ALL messages and tree structure.

### Knowledge Extraction Prompt Structure

The `extract_summaries` node in `knowledge_extraction` subgraph uses the tree/paths format to summarize user responses per sub-area. When leaf summaries are available (from `leaf_coverage` table), this LLM call is skipped entirely.

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
- `leaf_interview.py` - Quick evaluate, response generation
- `small_talk_response.py` - Small talk response
- `completed_area_response.py` - Completed area response
- `area_loop/nodes.py` - Area chat with tools
- `transcribe/extract_text.py` - Audio transcription

## Language Behavior

All user-facing prompts use the `_with_language_rule()` helper which prepends the language matching rule.

This applies to:
- `PROMPT_SMALL_TALK` - Greetings and app questions
- `build_area_chat_prompt()` - Area management
- `PROMPT_LEAF_QUESTION` - Initial leaf questions
- `PROMPT_LEAF_FOLLOWUP` - Follow-up questions
- `PROMPT_LEAF_COMPLETE` - Transition to next topic
- `PROMPT_LEAF_SUMMARY` - Summary extraction (preserves user's language in summaries)
- `PROMPT_ALL_LEAVES_DONE` - Completion message
- `PROMPT_COMPLETED_AREA` - Already-extracted area response

Internal prompts (classification, evaluation, extraction) remain English-only as they don't produce user-visible output.

The rule constant is defined once in `src/shared/prompts.py`:
```python
_RULE_MATCH_LANGUAGE = """\
**CRITICAL - LANGUAGE RULE:**
Detect the language of the user's LAST message and respond in that SAME language.
- If user writes in Russian → respond in Russian
- If user writes in English → respond in English
- If user writes in Spanish → respond in Spanish
- And so on for any language
DO NOT switch languages mid-conversation. Match the user's language exactly."""
```

## Known Limitations

1. **Token counting is approximate:** Uses character-based estimation (4 chars per token) rather than model-specific tokenizers for performance.

2. **Message trimming is by token budget:** Long messages may be trimmed mid-content. Consider summarization for very long histories.

3. **No streaming:** All LLM calls are blocking. For long responses, users wait for full completion.

4. **Provider-dependent behavior:** OpenRouter may have different rate limits or behaviors than direct API access.

5. **Reasoning models and structured output:** GPT-5.x "codex" models use reasoning tokens (internal thinking) before generating output. Without limits, they can consume all tokens on reasoning, causing `LengthFinishReasonError`. For structured output nodes, reasoning is minimized via `{"reasoning": {"effort": "low"}}`. Note: gpt-5.1-codex-mini only supports "low", "medium", "high" (not "none").

## LLMClientBuilder

The `LLMClientBuilder` dataclass (`src/infrastructure/ai.py`) standardizes LLM client creation:

```python
@dataclass
class LLMClientBuilder:
    model: str
    temperature: float | None = None
    max_tokens: int | None = None
    reasoning: dict | None = None
```

All parameters are passed through to ChatOpenAI. Use explicit temperatures for consistency.

The `reasoning` parameter controls reasoning effort for GPT-5.x models:
- `{"effort": "low"}` - Minimize reasoning for structured output
