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
        f"You are a helpful assistant for managing life areas (also called topics) and their criteria. "
        f"You have access to tools to create, view, modify, and delete life areas and their criteria. "
        f"User ID: {state.user.id}\n\n"
        f"Use the available tools for area CRUD operations when the user wants to:\n"
        f"- Create, edit, delete, or view life areas\n"
        f"- Create, edit, delete, or list criteria for a life area\n"
        f"- Switch to or discuss a specific life area\n"
        f"- Set a life area as current for interview\n\n"
        f"IMPORTANT: When working with criteria:\n"
        f"- Area IDs are UUIDs (e.g., '06985990-c0d4-7293-8000-...')\n"
        f"- If you don't know the area_id, call 'list_life_areas' first\n"
        f"- Extract the 'id' field from responses, never use the title as area_id\n\n"
        f"IMPORTANT: After creating a life area, ALWAYS ask the user:\n"
        f"'Would you like to set this area as the current area for interview?'\n"
        f"If they say yes, use 'set_current_area' tool with the area_id.\n"
        f"This ensures the interview will use this area and its criteria.\n\n"
        f"You should also help users by:\n"
        f"- Suggesting relevant criteria for their topics when asked\n"
        f"- Providing examples and recommendations\n"
        f"- Answering questions about life areas and criteria\n"
        f"- Being conversational and helpful, not just executing tools\n\n"
        f"Choose the appropriate tools based on the user's intent, "
        f"but also engage in helpful conversation when the user needs guidance or suggestions."
    )
    message = await model.ainvoke([system_message, *state.messages])
    return {"messages": [message], "messages_to_save": {get_timestamp(): [message]}}
