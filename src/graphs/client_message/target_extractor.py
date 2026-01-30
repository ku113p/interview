from dataclasses import dataclass
import os
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from src import db
from src.domain import user
from src.graphs.router.graph import Target


@dataclass
class Result:
    last_messages: list[BaseMessage]
    target: Target


class State(TypedDict):
    user: user.User
    text: str
    last_messages: list[BaseMessage] | None
    target: Target | None


async def extract_target(state: State):
    user_obj = state["user"]
    text = state["text"]

    prev_messages = get_formatted_history(user_obj)
    full_context = prev_messages + [HumanMessage(content=text)]

    target = (
        Target.from_user_mode(user_obj.mode)
        if user_obj.mode != user.InputMode.auto
        else await extract_target_from_messages(full_context)
    )

    return {"last_messages": full_context, "target": target}


class IntentClassification(BaseModel):
    target: Target = Field(..., description="The classified target mode.")


def get_formatted_history(user_obj: user.User, limit: int = 10) -> list[BaseMessage]:
    domain_msgs = [
        msg.data
        for msg
        in db.History.list_by_user(user_obj.id)
    ][-limit:]
    
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
    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )
    
    structured_llm = llm.with_structured_output(IntentClassification)

    system_prompt = SystemMessage(content=(
        "Classify the user intent based on conversation context.\n"
        "Return 'interview' for answering questions or continuing discussion.\n"
        "Return 'areas' for changing topics, settings, or stopping."
    ))

    messages_with_system = [system_prompt] + messages

    result = await structured_llm.ainvoke(messages_with_system)
    
    return result.target
