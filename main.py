import argparse
import asyncio
import logging
import uuid

from src.config.logging import configure_logging
from src.processes.auth import run_auth_pool
from src.processes.extract import run_extract_pool
from src.processes.interview import run_graph_pool
from src.processes.transport import parse_user_id, run_cli, run_telegram
from src.runtime import Channels
from src.workflows.subgraphs.transcribe.nodes.extract_audio import (
    check_ffmpeg_availability,
)


async def run_application(transport: str, user_id: uuid.UUID) -> None:
    """Start transport and worker pools."""
    channels = Channels()

    tasks = [
        run_graph_pool(channels),
        run_extract_pool(channels),
    ]

    if transport == "cli":
        tasks.append(run_cli(channels, user_id))
    elif transport == "telegram":
        tasks.append(run_auth_pool(channels))
        tasks.append(run_telegram(channels))

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        channels.shutdown.set()


def main() -> None:
    configure_logging(level=logging.INFO, use_json=True)
    check_ffmpeg_availability()
    parser = argparse.ArgumentParser(description="Interview CLI")
    parser.add_argument(
        "--transport",
        default="cli",
        choices=["cli", "telegram"],
        help="Select the transport backend",
    )
    parser.add_argument(
        "--user-id",
        type=parse_user_id,
        default=parse_user_id(None),
        help="Use an existing user UUID for the session",
    )

    args = parser.parse_args()

    try:
        asyncio.run(run_application(args.transport, args.user_id))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" in str(exc):
            raise RuntimeError(
                "Event loop already running. Call run_application() directly in async context."
            ) from exc
        raise


if __name__ == "__main__":
    main()
