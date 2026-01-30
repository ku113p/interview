import os
import base64
from tempfile import NamedTemporaryFile
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


class State(TypedDict):
    audio_file: NamedTemporaryFile
    text: str | None


async def extract_text(state: State):
    audio_file = state["audio_file"]
    text = await extract_text_from_audio(audio_file)
    return {"text": text}


async def extract_text_from_audio(audio_file: NamedTemporaryFile) -> str:
    audio_file.seek(0)
    audio_data = audio_file.read()
    b64_audio = base64.b64encode(audio_data).decode("utf-8")

    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )

    message = HumanMessage(
        content=[
            {
                "type": "text", 
                "text": "Transcribe this audio verbatim."
            },
            {
                "type": "input_audio",
                "input_audio": {
                    "data": b64_audio,
                    "format": "mp3"
                }
            }
        ]
    )

    response = await llm.ainvoke([message])
    return response.content
