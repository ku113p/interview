"""Command handling node for the main workflow."""

from langchain_core.messages import AIMessage

from src.processes.interview import State

from .handlers import process_command


async def handle_command(state: State) -> dict:
    """Check for commands and handle them.

    If text starts with '/', attempts to process as a command.
    Returns command_response and adds to messages if handled.
    """
    response = await process_command(state.text.strip(), state.user)

    if response is None:
        # Not a command or unknown command - continue normal workflow
        return {"command_response": None}

    # Command handled - return response and add to messages
    return {
        "command_response": response,
        "messages": [AIMessage(content=response)],
    }
