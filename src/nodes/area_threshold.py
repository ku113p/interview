from typing_extensions import TypedDict

from typing_extensions import TypedDict

from langchain_core.messages import AIMessage


class State(TypedDict):
    messages: list


def area_threshold(*args, **kwargs):
    content = "Can you say this differently? (answer generation error)"
    ai_msg = AIMessage(content=content)
    return {"messages": [ai_msg]}
