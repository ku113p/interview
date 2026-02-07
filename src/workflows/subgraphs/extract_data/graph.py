"""Extract data workflow graph."""

from functools import partial

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from .nodes import extract_summaries, load_area_data, save_extracted_data
from .state import ExtractDataState


def build_extract_data_graph(llm: ChatOpenAI):
    """Build the extract_data workflow graph.

    This graph:
    1. Loads area data (title, criteria, messages)
    2. Uses LLM to extract summaries for each criterion
    3. Saves the extracted data to the database

    Args:
        llm: LLM client for extraction

    Returns:
        Compiled LangGraph workflow
    """
    builder = StateGraph(ExtractDataState)

    builder.add_node("load_area_data", load_area_data)
    builder.add_node("extract_summaries", partial(extract_summaries, llm=llm))
    builder.add_node("save_extracted_data", save_extracted_data)

    builder.add_edge(START, "load_area_data")
    builder.add_edge("load_area_data", "extract_summaries")
    builder.add_edge("extract_summaries", "save_extracted_data")
    builder.add_edge("save_extracted_data", END)

    return builder.compile()
