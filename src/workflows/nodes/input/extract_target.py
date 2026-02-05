from typing import Annotated

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.application.state import Target
from src.domain.models import InputMode, User


class State(BaseModel):
    user: User
    messages: Annotated[list[BaseMessage], add_messages]
    target: Target | None


async def extract_target(state: State, llm: ChatOpenAI):
    user_obj = state.user

    if user_obj.mode != InputMode.auto:
        target = Target.from_user_mode(user_obj.mode)
    elif user_obj.current_life_area_id is not None:
        target = Target.interview
    else:
        target = await extract_target_from_messages(state.messages, llm)

    return {"target": target}


class IntentClassification(BaseModel):
    target: Target = Field(..., description="The classified target mode.")


async def extract_target_from_messages(
    messages: list[BaseMessage], llm: ChatOpenAI
) -> Target:
    structured_llm = llm.with_structured_output(IntentClassification)

    system_prompt = SystemMessage(
        content=(
            "Classify the user intent based on conversation context.\n"
            "Return 'interview' for answering questions or continuing discussion.\n"
            "Return 'areas' for changing topics, settings, or stopping."
        )
    )

    messages_with_system = [system_prompt] + messages

    result = await structured_llm.ainvoke(messages_with_system)

    if isinstance(result, dict):
        return Target(result["target"])

    return result.target
