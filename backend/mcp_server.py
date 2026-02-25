"""Standalone entry point for the MCP server."""

import argparse

from src.processes.mcp_server import run_server

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interview Assistant MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=8080, help="Port number")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)
