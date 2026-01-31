from src import graph
from src.cli.session import run_cli
from src.graphs.deps import build_default_deps


def main():
    deps = build_default_deps()
    runner = graph.get_graph(deps).ainvoke
    run_cli(runner)


if __name__ == "__main__":
    main()
