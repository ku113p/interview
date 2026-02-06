from typing import Annotated

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.application.state import Target
from src.domain.models import InputMode, User
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

    system_prompt = SystemMessage(
        content=(
            "You are a routing classifier. Analyze the user's message and determine which module should handle it.\n\n"
            "**Return 'areas' when the user wants to:**\n"
            "- Manage life areas (also called topics) or their evaluation criteria\n"
            "- Use any of these area management operations:\n"
            f"{areas_tools_desc}\n"
            "- Ask questions about criteria setup (e.g., 'what criteria should we use?', 'which criteria can we create?')\n"
            "- Discuss area/criteria configuration or management\n\n"
            "**Return 'interview' when the user wants to:**\n"
            "- Share experiences, stories, or information about a topic\n"
            "- Answer questions about their background or skills\n"
            "- Have a conversation to evaluate their knowledge/experience\n"
            "- Respond to interview questions\n\n"
            "**Key distinction:**\n"
            "- 'areas' = managing the structure (what to evaluate, setup, configuration)\n"
            "- 'interview' = the actual conversation (being evaluated, sharing experiences)\n\n"
            "Classify based on message intent only, ignoring conversation history."
        )
    )

    messages_with_system = [system_prompt] + messages

    result = await structured_llm.ainvoke(messages_with_system)

    if isinstance(result, dict):
        return Target(result["target"])

    return result.target
