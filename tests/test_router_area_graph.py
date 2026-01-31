import pytest
from typing import cast

from langchain_core.messages import AIMessage

from src.graphs.router.area.graph import get_subgraph, build_tool_messages
from src.graphs.deps import Deps


@pytest.mark.anyio
async def test_area_graph_requires_loop_step():
    graph = get_subgraph(build_stub_deps())
    state = {"messages": [AIMessage(content="hi", tool_calls=[])]}
    with pytest.raises(KeyError):
        await graph.ainvoke(state)


@pytest.mark.anyio
async def test_area_graph_preserves_loop_step():
    graph = get_subgraph(build_stub_deps())
    state = {"loop_step": 2, "messages": [AIMessage(content="hi", tool_calls=[])]}
    result = await graph.ainvoke(state)
    assert result["loop_step"] == 2


def build_stub_deps() -> Deps:
    class StubLLM:
        def bind_tools(self, tools):
            class Runner:
                async def ainvoke(self, _):
                    return [AIMessage(content="ok", tool_calls=[])]

            return Runner()

    def build_llm(temperature: float | None = None):  # noqa: ARG001
        return StubLLM()

    deps = {"build_llm": build_llm, "get_area_tools": lambda: []}
    return cast(Deps, deps)


@pytest.mark.anyio
async def test_build_tool_messages_awaits_tool():
    called = {"value": False}

    class StubTool:
        name = "stub"

        async def ainvoke(self, args):
            called["value"] = True
            return {"echo": args}

    deps = cast(Deps, {"get_area_tools": lambda: [StubTool()]})

    message = AIMessage(
        content="tool",
        tool_calls=[{"id": "1", "name": "stub", "args": {"foo": "bar"}}],
    )

    result = await build_tool_messages(message, deps)

    assert called["value"] is True
    assert result[0].content == str({"echo": {"foo": "bar"}})
