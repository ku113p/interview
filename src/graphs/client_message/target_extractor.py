import os
from typing import cast
from typing_extensions import NotRequired, TypedDict
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from src import db
from src.domain import user
from src.graphs.router.graph import Target


class State(TypedDict):
    user: user.User
    text: str
    messages: NotRequired[list[BaseMessage]]
    target: NotRequired[Target]


async def extract_target(state: State):
    user_obj = state["user"]
    text = state["text"]
    prev_messages, use_history = resolve_messages(state, user_obj)
    new_message = HumanMessage(content=text)
    full_context = prev_messages + [new_message]
    target = await get_target(user_obj, full_context)
    return build_updates(use_history, full_context, new_message, target)


def resolve_messages(state: State, user_obj: user.User):
    existing_messages = state.get("messages")
    if existing_messages is None:
        return get_formatted_history(user_obj), True
    return existing_messages, False


async def get_target(user_obj: user.User, messages: list[BaseMessage]):
    if user_obj.mode != user.InputMode.auto:
        return Target.from_user_mode(user_obj.mode)
    return await extract_target_from_messages(messages)


def build_updates(
    use_history: bool,
    full_context: list[BaseMessage],
    new_message: BaseMessage,
    target: Target,
):
    messages_update = full_context if use_history else [new_message]
    return {"target": target, "messages": messages_update}


class IntentClassification(BaseModel):
    target: Target = Field(..., description="The classified target mode.")


def get_formatted_history(user_obj: user.User, limit: int = 10) -> list[BaseMessage]:
    domain_msgs = [msg.data for msg in db.History.list_by_user(user_obj.id)][-limit:]

    formatted_messages = []
    for msg in domain_msgs:
        if msg["role"] == "user":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            formatted_messages.append(AIMessage(content=msg["content"]))
        else:
            raise NotImplementedError()

    return formatted_messages


async def extract_target_from_messages(messages: list[BaseMessage]) -> Target:
    structured_llm = build_structured_llm()
    system_prompt = build_system_prompt()
    result = await structured_llm.ainvoke([system_prompt] + messages)
    parsed = cast(IntentClassification, result)
    return parsed.target


def build_structured_llm():
    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        api_key=get_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )
    return llm.with_structured_output(IntentClassification)


def get_api_key() -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise ValueError("OPENROUTER_API_KEY is required")
    return api_key


def build_system_prompt():
    return SystemMessage(
        content=(
            "Classify the user intent based on conversation context.\n"
            "Return 'interview' for answering questions or continuing discussion.\n"
            "Return 'areas' for changing topics, settings, or stopping."
        )
    )
