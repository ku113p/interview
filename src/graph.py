from functools import partial

from langgraph.graph import END, START, StateGraph

from src.ai import NewAI
from src.nodes.extract_target import extract_target
from src.nodes.interview import interview
from src.routers.message_router import route_message
from src.state import State
from src.subgraph.area_loop.flow import MAX_AREA_RECURSION
from src.subgraph.area_loop.graph import build_area_graph
from src.subgraph.extract_flow.graph import build_extract_graph

MODEL_NAME_FLASH = "google/gemini-2.0-flash-001"


def get_graph():
    builder = StateGraph(State)
    extract_graph = build_extract_graph(NewAI(MODEL_NAME_FLASH, 0).build())
    builder.add_node("extract_text", extract_graph)
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
