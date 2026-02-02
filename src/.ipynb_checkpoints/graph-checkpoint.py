import asyncio
import uuid
from functools import partial
from typing import Annotated, BinaryIO

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, ConfigDict

from langgraph.graph import START, END, StateGraph

from src.ai import NewAI
from src.domain import message, user
from src.nodes.extract_audio import State as ExtractAudioState, extract_audio
from src.nodes.extract_target import extract_target
from src.nodes.extract_text import extract_text_from_message
from src.nodes.interview import interview
from src.subgraph.area_loop.flow import MAX_AREA_RECURSION
from src.subgraph.area_loop.graph import build_area_graph
from src.routers.message_router import route_message, Target


MODEL_NAME_FLASH = "google/gemini-2.0-flash-001"


class State(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user: user.User
    message: message.ClientMessage
    media_file: BinaryIO
    audio_file: BinaryIO
    text: str
    target: Target
    messages: Annotated[list[BaseMessage], add_messages]
    area_id: uuid.UUID
    extract_data_tasks: asyncio.Queue[uuid.UUID]
    was_covered: bool


async def extract_text(state: State, llm: ChatOpenAI):
    c_msg = state.message
    if isinstance(c_msg.data, str):
        return {"text": c_msg.data}

    audio_state = await extract_audio(
        ExtractAudioState(
            message=c_msg.data,
            media_file=state.media_file,
            audio_file=state.audio_file,
        )
    )
    text = await extract_text_from_message(audio_state["audio_file"], llm)
    return {"text": text}


def get_graph():
    builder = StateGraph(State)

    builder.add_node(
        "extract_text",
        partial(extract_text, llm=NewAI(MODEL_NAME_FLASH, 0).build()),
    )
    builder.add_node(
        "extract_target",
        partial(extract_target, llm=NewAI(MODEL_NAME_FLASH, 0).build()),
    )
    builder.add_node(
        "interview", partial(interview, llm=NewAI(MODEL_NAME_FLASH).build())
    )

    area_graph = build_area_graph(NewAI(MODEL_NAME_FLASH).build()).with_config(
        {"recursion_limit": MAX_AREA_RECURSION}
    )

    builder.add_node("area_loop", area_graph)

    builder.add_edge(START, "extract_text")
    builder.add_edge("extract_text", "extract_target")
    builder.add_conditional_edges("extract_target", route_message)

    builder.add_edge("interview", END)

    builder.add_edge("area_loop", END)

    return builder.compile()
