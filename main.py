import argparse
import asyncio
import logging

from src.cli.session import parse_user_id, run_cli_async
from src.logging_config import configure_logging
from src.subgraph.extract_flow.nodes.extract_audio import check_ffmpeg_availability


def main() -> None:
    configure_logging(level=logging.INFO, use_json=True)
    check_ffmpeg_availability()
    parser = argparse.ArgumentParser(description="Interview CLI")
    parser.add_argument(
        "--transport",
        default="cli",
        choices=["cli", "http", "mcp"],
        help="Select the transport backend",
    )
    parser.add_argument(
        "--user-id",
        type=parse_user_id,
        default=parse_user_id(None),
        help="Use an existing user UUID for the session",
    )

    args = parser.parse_args()
    if args.transport != "cli":
        raise RuntimeError(f"Transport not implemented: {args.transport}")

    try:
        asyncio.run(run_cli_async(args.user_id))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" in str(exc):
            raise RuntimeError(
                "Event loop already running. Use run_cli_async() in an async context."
            ) from exc
        raise


if __name__ == "__main__":
    main()
