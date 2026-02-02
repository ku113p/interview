from functools import partial
from typing import Annotated
from pydantic import BaseModel

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from src.subgraph.area_loop.flow import route_area
from src.subgraph.area_loop.nodes.area_chat import area_chat
from src.subgraph.area_loop.nodes.area_end import area_end
from src.subgraph.area_loop.nodes.area_threshold import area_threshold
from src.subgraph.area_loop.nodes.area_tools import area_tools


class AreaState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]


def build_area_graph(llm):
    area_builder = StateGraph(AreaState)
    area_builder.add_node("area_chat", partial(area_chat, llm=llm))
    area_builder.add_node("area_tools", area_tools)
    area_builder.add_node("area_threshold", area_threshold)
    area_builder.add_node("area_end", area_end)

    area_builder.set_entry_point("area_chat")
    area_builder.add_conditional_edges(
        "area_chat", route_area, ["area_tools", "area_threshold", "area_end"]
    )
    area_builder.add_edge("area_tools", "area_chat")
    area_builder.set_finish_point("area_threshold")
    area_builder.set_finish_point("area_end")
    return area_builder.compile()
