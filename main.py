import argparse
import asyncio
import logging
import uuid

from src.application.workers.channels import Channels
from src.application.workers.cli_worker import parse_user_id, run_cli_pool
from src.application.workers.extract_worker import run_extract_pool
from src.application.workers.graph_worker import run_graph_pool
from src.config.logging import configure_logging
from src.workflows.subgraphs.transcribe.nodes.extract_audio import (
    check_ffmpeg_availability,
)


async def run_all_pools(transport: str, user_id: uuid.UUID) -> None:
    """Start all worker pools as peers."""
    channels = Channels()

    pools = [
        run_graph_pool(channels),
        run_extract_pool(channels),
    ]

    # Add transport pool based on selection
    if transport == "cli":
        pools.append(run_cli_pool(channels, user_id))
    # Future: elif transport == "http": pools.append(run_http_pool(channels))

    try:
        await asyncio.gather(*pools)
    except asyncio.CancelledError:
        channels.shutdown.set()


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
        asyncio.run(run_all_pools(args.transport, args.user_id))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" in str(exc):
            raise RuntimeError(
                "Event loop already running. Call run_all_pools() directly in async context."
            ) from exc
        raise


if __name__ == "__main__":
    main()
