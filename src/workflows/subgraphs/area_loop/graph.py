from functools import partial
from typing import Annotated

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.workflows.subgraphs.area_loop.flow import route_area
from src.workflows.subgraphs.area_loop.nodes.area_chat import area_chat
from src.workflows.subgraphs.area_loop.nodes.area_end import area_end
from src.workflows.subgraphs.area_loop.nodes.area_tools import area_tools


class AreaState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    success: bool | None = None


def build_area_graph(llm: ChatOpenAI):
    area_builder = StateGraph(AreaState)
    area_builder.add_node("area_chat", partial(area_chat, llm=llm))
    area_builder.add_node("area_tools", area_tools)
    area_builder.add_node("area_end", area_end)
    area_builder.add_edge(START, "area_chat")
    area_builder.add_conditional_edges(
        "area_chat", route_area, ["area_tools", "area_end"]
    )
    area_builder.add_edge("area_tools", "area_chat")
    area_builder.add_edge("area_end", END)
    return area_builder.compile()
