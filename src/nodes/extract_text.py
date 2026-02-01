import os
import base64
from typing import BinaryIO
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


async def extract_text_from_audio(audio_file: BinaryIO) -> str:
    audio_file.seek(0)
    audio_data = audio_file.read()
    b64_audio = base64.b64encode(audio_data).decode("utf-8")

    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Transcribe this audio verbatim."},
            {
                "type": "input_audio",
                "input_audio": {"data": b64_audio, "format": "mp3"},
            },
        ]
    )

    response = await llm.ainvoke([message])
    if isinstance(response.content, str):
        return response.content
    if isinstance(response.content, list):
        return "".join(str(part) for part in response.content)
    return str(response.content)


async def extract_text_from_message(message_data: str | BinaryIO) -> str:
    if isinstance(message_data, str):
        return message_data
    return await extract_text_from_audio(message_data)
