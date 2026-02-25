import base64

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.shared.prompts import PROMPT_TRANSCRIBE
from src.shared.retry import invoke_with_retry
from src.shared.utils.content import normalize_content

from ..file_utils import read_file_bytes


async def extract_text_from_audio(audio_file_path: str, llm: ChatOpenAI) -> str:
    audio_data = await read_file_bytes(audio_file_path)
    if not audio_data:
        raise ValueError("Audio file is empty")
    b64_audio = base64.b64encode(audio_data).decode("utf-8")

    message = HumanMessage(
        content=[
            {"type": "text", "text": PROMPT_TRANSCRIBE},
            {
                "type": "input_audio",
                "input_audio": {"data": b64_audio, "format": "wav"},
            },
        ]
    )

    response = await invoke_with_retry(lambda: llm.ainvoke([message]))
    return normalize_content(response.content)


async def extract_text_from_message(audio_file_path: str, llm: ChatOpenAI) -> str:
    """Extract text from an audio file by transcribing it.

    Args:
        audio_file_path: Path to the audio file to transcribe
        llm: ChatOpenAI instance for transcription

    Returns:
        Transcribed text from the audio file
    """
    return await extract_text_from_audio(audio_file_path, llm)
