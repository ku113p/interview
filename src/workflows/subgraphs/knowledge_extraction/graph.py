"""Extract data workflow graph."""

from functools import partial

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from .nodes import (
    extract_knowledge,
    extract_summaries,
    load_area_data,
    save_knowledge,
    save_summary,
)
from .routers import route_extraction_success, route_has_data
from .state import KnowledgeExtractionState


def build_knowledge_extraction_graph(
    llm: ChatOpenAI, knowledge_llm: ChatOpenAI | None = None
):
    """Build the knowledge_extraction workflow graph.

    This graph:
    1. Loads area data (title, criteria, messages)
    2. Routes based on whether there's data to process
    3. Uses LLM to extract summaries for each criterion
    4. Routes based on extraction success
    5. Generates embedding and saves summary to area_summaries
    6. Extracts knowledge (skills/facts) from the summary
    7. Saves knowledge items with area links

    Args:
        llm: LLM client for summary extraction
        knowledge_llm: Optional LLM for knowledge extraction (defaults to llm)

    Returns:
        Compiled LangGraph workflow
    """
    knowledge_llm = knowledge_llm or llm
    builder = StateGraph(KnowledgeExtractionState)

    # Add nodes
    builder.add_node("load_area_data", load_area_data)
    builder.add_node("extract_summaries", partial(extract_summaries, llm=llm))
    builder.add_node("save_summary", save_summary)
    builder.add_node("extract_knowledge", partial(extract_knowledge, llm=knowledge_llm))
    builder.add_node("save_knowledge", save_knowledge)

    # Define flow with conditional routing
    builder.add_edge(START, "load_area_data")
    builder.add_conditional_edges("load_area_data", route_has_data)
    builder.add_conditional_edges("extract_summaries", route_extraction_success)
    builder.add_edge("save_summary", "extract_knowledge")
    builder.add_edge("extract_knowledge", "save_knowledge")
    builder.add_edge("save_knowledge", END)

    return builder.compile()
