import base64
import os
from tempfile import _TemporaryFileWrapper
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


class State(TypedDict):
    audio_file: _TemporaryFileWrapper[bytes]
    text: str | None


async def extract_text(state: State):
    audio_file = state["audio_file"]
    text = await extract_text_from_audio(audio_file)
    return {"text": text}


async def extract_text_from_audio(audio_file: _TemporaryFileWrapper[bytes]) -> str:
    b64_audio = encode_audio(audio_file)
    llm = build_llm()
    message = build_prompt(b64_audio)
    response = await llm.ainvoke([message])
    return parse_transcription(response.content)


def encode_audio(audio_file: _TemporaryFileWrapper[bytes]) -> str:
    audio_file.seek(0)
    audio_data = audio_file.read()
    return base64.b64encode(audio_data).decode("utf-8")


def build_llm():
    return ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        api_key=get_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )


def build_prompt(b64_audio: str):
    return HumanMessage(
        content=[
            {"type": "text", "text": "Transcribe this audio verbatim."},
            {
                "type": "input_audio",
                "input_audio": {"data": b64_audio, "format": "mp3"},
            },
        ]
    )


def parse_transcription(content: object) -> str:
    if not isinstance(content, str):
        raise ValueError("Transcription failed")
    return content


def get_api_key() -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise ValueError("OPENROUTER_API_KEY is required")
    return api_key
