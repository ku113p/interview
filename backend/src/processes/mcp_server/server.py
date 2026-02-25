"""MCP server entry point (Streamable HTTP)."""


def run_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Start the MCP server on the given host and port."""
    from .tools import mcp

    mcp.run(transport="streamable-http", host=host, port=port)
