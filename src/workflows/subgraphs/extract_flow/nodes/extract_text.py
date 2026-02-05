import base64
from typing import BinaryIO

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.shared.utils.content import normalize_content


async def extract_text_from_audio(audio_file: BinaryIO, llm: ChatOpenAI) -> str:
    audio_file.seek(0)
    audio_data = audio_file.read()
    if not audio_data:
        raise ValueError("Audio file is empty")
    b64_audio = base64.b64encode(audio_data).decode("utf-8")

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Transcribe this audio verbatim."},
            {
                "type": "input_audio",
                "input_audio": {"data": b64_audio, "format": "wav"},
            },
        ]
    )

    response = await llm.ainvoke([message])
    return normalize_content(response.content)


async def extract_text_from_message(
    message_data: str | BinaryIO, llm: ChatOpenAI
) -> str:
    if isinstance(message_data, str):
        return message_data
    return await extract_text_from_audio(message_data, llm)
