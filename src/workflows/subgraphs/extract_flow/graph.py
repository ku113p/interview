from functools import partial

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ConfigDict

from src.domain.models import ClientMessage

from .nodes.extract_audio import State as ExtractAudioState
from .nodes.extract_audio import extract_audio
from .nodes.extract_text import extract_text_from_message


class ExtractState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    message: ClientMessage
    media_file: str
    audio_file: str
    text: str


def route_extract(state: ExtractState) -> str:
    c_msg = state.message
    if isinstance(c_msg.data, str):
        return "extract_text"
    return "extract_audio"


async def run_extract_audio(state: ExtractState):
    c_msg = state.message
    await extract_audio(
        ExtractAudioState(
            message=c_msg.data,
            media_file=state.media_file,
            audio_file=state.audio_file,
        )
    )
    return {}


async def extract_text(state: ExtractState, llm: ChatOpenAI):
    c_msg = state.message
    if isinstance(c_msg.data, str):
        return {"text": c_msg.data}

    text = await extract_text_from_message(state.audio_file, llm)
    return {"text": text}


def build_extract_graph(llm: ChatOpenAI):
    builder = StateGraph(ExtractState)
    builder.add_node("extract_audio", run_extract_audio)
    builder.add_node("extract_text", partial(extract_text, llm=llm))
    builder.add_conditional_edges(
        START, route_extract, ["extract_text", "extract_audio"]
    )
    builder.add_edge("extract_audio", "extract_text")
    builder.add_edge("extract_text", END)
    return builder.compile()
