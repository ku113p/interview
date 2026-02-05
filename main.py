import argparse
import asyncio
import logging

from src.adapters.cli.session import parse_user_id, run_cli_async
from src.config.logging import configure_logging
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
        raise RuntimeError(f"Transport '{args.transport}' not supported. Use: cli")

    try:
        asyncio.run(run_cli_async(args.user_id))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" in str(exc):
            raise RuntimeError(
                "Event loop already running. Call run_cli_async() directly in async context."
            ) from exc
        raise


if __name__ == "__main__":
    main()
