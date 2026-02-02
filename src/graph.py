import asyncio
import uuid
from functools import partial
from typing import Annotated, BinaryIO

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from langgraph.graph import START, END, StateGraph

from src.ai import NewAI
from src.domain import message, user
from src.nodes.area_chat import area_chat
from src.nodes.area_threshold import area_threshold
from src.nodes.area_end import area_end
from src.nodes.area_tools import area_tools
from src.nodes.extract_audio import extract_audio
from src.nodes.extract_target import extract_target
from src.nodes.extract_text import extract_text_from_message
from src.nodes.interview import interview
from src.routers.area_router import route_area
from src.routers.message_router import route_message, Target


MODEL_NAME_FLASH = "google/gemini-2.0-flash-001"


class State(BaseModel):
    user: user.User
    message: message.ClientMessage
    media_file: BinaryIO
    audio_file: BinaryIO
    text: str
    target: Target
    loop_step: int
    messages: Annotated[list[BaseMessage], add_messages]
    area_id: uuid.UUID
    extract_data_tasks: asyncio.Queue[uuid.UUID]
    was_covered: bool


async def extract_text(state: State, llm: ChatOpenAI):
    c_msg = state.message
    if isinstance(c_msg.data, str):
        return {"text": c_msg.data}

    audio_state = await extract_audio(
        {
            "message": c_msg.data,
            "media_file": state.media_file,
            "audio_file": state.audio_file,
        }
    )
    text = await extract_text_from_message(audio_state["audio_file"], llm)
    return {"text": text}


def get_graph():
    builder = StateGraph(State)

    builder.add_node(
        "extract_text", partial(extract_text, NewAI(MODEL_NAME_FLASH, 0).build())
    )
    builder.add_node(
        "extract_target", partial(extract_target, NewAI(MODEL_NAME_FLASH, 0).build())
    )
    builder.add_node("interview", partial(interview, NewAI(MODEL_NAME_FLASH).build()))
    builder.add_node("area_chat", partial(area_chat, NewAI(MODEL_NAME_FLASH).build()))
    builder.add_node("area_tools", area_tools)
    builder.add_node("area_threshold", area_threshold)
    builder.add_node("area_end", area_end)

    builder.add_edge(START, "extract_text")
    builder.add_edge("extract_text", "extract_target")
    builder.add_conditional_edges("extract_target", route_message)

    builder.add_edge("interview", END)

    builder.add_conditional_edges(
        "area_chat", route_area, ["area_tools", "area_threshold", "area_end"]
    )
    builder.add_edge("area_tools", "area_chat")
    builder.add_edge("area_threshold", END)
    builder.add_edge("area_end", END)

    return builder.compile()
