import logging
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.timestamp import get_timestamp
from src.subgraph.area_loop.tools import AREA_TOOLS

logger = logging.getLogger(__name__)


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    success: bool | None = None


async def area_chat(state: State, llm):
    logger.info("Running area chat", extra={"message_count": len(state.messages)})
    model = llm.bind_tools(AREA_TOOLS)
    message = await model.ainvoke(state.messages)
    return {"messages": [message], "messages_to_save": {get_timestamp(): [message]}}
