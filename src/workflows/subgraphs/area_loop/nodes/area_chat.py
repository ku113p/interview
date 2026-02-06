import logging
from typing import Annotated

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.domain.models import User
from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.timestamp import get_timestamp
from src.workflows.subgraphs.area_loop.tools import AREA_TOOLS

logger = logging.getLogger(__name__)


class State(BaseModel):
    user: User
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    success: bool | None = None


async def area_chat(state: State, llm):
    logger.info("Running area chat", extra={"message_count": len(state.messages)})
    model = llm.bind_tools(AREA_TOOLS)
    system_message = SystemMessage(
        f"You are helping a user manage their life areas (also called topics). "
        f"You have access to tools to create, view, modify, and delete life areas and their criteria. "
        f"User ID: {state.user.id}\n\n"
        f"Use the available tools for area CRUD operations when the user wants to:\n"
        f"- Create, edit, delete, or view life areas\n"
        f"- Create, edit, delete, or list criteria for a life area\n"
        f"- Switch to or discuss a specific life area\n\n"
        f"Choose the appropriate tools based on the user's intent."
    )
    message = await model.ainvoke([system_message, *state.messages])
    return {"messages": [message], "messages_to_save": {get_timestamp(): [message]}}
