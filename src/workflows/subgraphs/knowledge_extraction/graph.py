"""Extract data workflow graph."""

from functools import partial

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from .nodes import (
    extract_knowledge,
    extract_summaries,
    load_area_data,
    persist_extraction,
    prepare_summary,
)
from .routers import route_extraction_success, route_has_data
from .state import KnowledgeExtractionState


def _add_extraction_edges(builder: StateGraph) -> None:
    """Add edges for the knowledge extraction workflow."""
    builder.add_edge(START, "load_area_data")
    builder.add_conditional_edges("load_area_data", route_has_data)
    builder.add_conditional_edges("extract_summaries", route_extraction_success)
    builder.add_edge("prepare_summary", "extract_knowledge")
    builder.add_edge("extract_knowledge", "persist_extraction")
    builder.add_edge("persist_extraction", END)


def build_knowledge_extraction_graph(
    llm: ChatOpenAI, knowledge_llm: ChatOpenAI | None = None
):
    """Build the knowledge_extraction workflow graph.

    This graph:
    1. Loads area data (title, sub-areas, messages/summaries)
    2. Routes based on whether there's data to process
    3. Uses LLM to extract summaries for each sub-area (skipped when leaf summaries exist)
    4. Routes based on extraction success
    5. Generates embedding vector for combined summary
    6. Extracts knowledge (skills/facts) from the summary
    7. Persists vector + knowledge + mark_extracted atomically

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
    builder.add_node("prepare_summary", prepare_summary)
    builder.add_node("extract_knowledge", partial(extract_knowledge, llm=knowledge_llm))
    builder.add_node("persist_extraction", persist_extraction)

    _add_extraction_edges(builder)
    return builder.compile()
