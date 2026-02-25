"""Knowledge extraction workflow graph."""

from functools import partial

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from .nodes import (
    extract_knowledge,
    load_summary,
    persist_extraction,
    vectorize_summary,
)
from .state import KnowledgeExtractionState


def _route_after_load(state: KnowledgeExtractionState) -> str:
    return "vectorize_summary" if state.summary_text else "__end__"


def build_knowledge_extraction_graph(llm: ChatOpenAI):
    """Build the knowledge_extraction workflow graph.

    Linear 4-node pipeline:
    1. load_summary: loads summary text and area_id from DB
    2. vectorize_summary: generates embedding vector
    3. extract_knowledge: extracts skills/facts from summary text
    4. persist_extraction: saves vector + knowledge items atomically

    Args:
        llm: LLM client for knowledge extraction

    Returns:
        Compiled LangGraph workflow
    """
    builder = StateGraph(KnowledgeExtractionState)

    builder.add_node("load_summary", load_summary)
    builder.add_node("vectorize_summary", vectorize_summary)
    builder.add_node("extract_knowledge", partial(extract_knowledge, llm=llm))
    builder.add_node("persist_extraction", persist_extraction)

    builder.add_edge(START, "load_summary")
    builder.add_conditional_edges("load_summary", _route_after_load)
    builder.add_edge("vectorize_summary", "extract_knowledge")
    builder.add_edge("extract_knowledge", "persist_extraction")
    builder.add_edge("persist_extraction", END)

    return builder.compile()
