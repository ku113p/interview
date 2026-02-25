"""MCP server process: read-only data tools over Streamable HTTP."""


# Lazy import to avoid pulling in server/tools at package import time
def run_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Start the MCP server on the given host and port."""
    from src.processes.mcp_server.server import run_server as _run_server

    _run_server(host=host, port=port)


__all__ = ["run_server"]
