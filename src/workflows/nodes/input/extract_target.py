from typing import Annotated

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.application.state import Target
from src.config.settings import HISTORY_LIMIT_EXTRACT_TARGET
from src.domain.models import InputMode, User
from src.shared.prompts import build_extract_target_prompt
from src.shared.retry import invoke_with_retry
from src.workflows.subgraphs.area_loop.tools import AREA_TOOLS


class State(BaseModel):
    user: User
    messages: Annotated[list[BaseMessage], add_messages]
    target: Target | None


async def extract_target(state: State, llm: ChatOpenAI):
    user_obj = state.user

    if user_obj.mode != InputMode.auto:
        target = Target.from_user_mode(user_obj.mode)
    else:
        target = await extract_target_from_messages(state.messages, llm)

    return {"target": target}


class IntentClassification(BaseModel):
    target: Target = Field(..., description="The classified target mode.")


def _generate_areas_tools_description(tools: list[BaseTool]) -> str:
    """Generate description of available area management tools."""
    tool_descriptions = []
    for tool in tools:
        # Extract tool name and description
        name = tool.name
        desc = tool.description or ""
        tool_descriptions.append(f"  - {name}: {desc}")

    return "\n".join(tool_descriptions)


async def extract_target_from_messages(
    messages: list[BaseMessage], llm: ChatOpenAI
) -> Target:
    structured_llm = llm.with_structured_output(IntentClassification)

    # Auto-generate tools description from AREA_TOOLS
    areas_tools_desc = _generate_areas_tools_description(AREA_TOOLS)
    prompt_content = build_extract_target_prompt(areas_tools_desc)
    system_prompt = SystemMessage(content=prompt_content)

    # Use only last N messages for classification (limit context for extract_target)
    recent_messages = messages[-HISTORY_LIMIT_EXTRACT_TARGET:]
    messages_with_system = [system_prompt] + recent_messages

    result = await invoke_with_retry(
        lambda: structured_llm.ainvoke(messages_with_system)
    )

    if isinstance(result, dict):
        return Target(result["target"])

    return result.target
