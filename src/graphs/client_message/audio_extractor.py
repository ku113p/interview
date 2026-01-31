import asyncio
import io
from tempfile import _TemporaryFileWrapper
from typing_extensions import TypedDict
from src.domain import message


class State(TypedDict):
    message: message.ClientMessage
    media_file: _TemporaryFileWrapper[bytes]
    audio_file: _TemporaryFileWrapper[bytes]


async def extract_audio(state: State):
    c_msg = state["message"]
    m_file = state["media_file"]

    if isinstance(c_msg.data, str):
        raise ValueError("Expected media message")

    await write_file(m_file, c_msg.data.content)

    if c_msg.data.type == message.MessageType.audio:
        return {"audio_file": m_file}

    await extract_audio_from_video(m_file, state["audio_file"])
    return {"audio_file": state["audio_file"]}


async def write_file(tmp_file: _TemporaryFileWrapper[bytes], stream: io.BytesIO):
    tmp_file.seek(0)
    tmp_file.write(stream.read())
    tmp_file.seek(0)
    return tmp_file


async def extract_audio_from_video(
    media_tmp_file: _TemporaryFileWrapper[bytes],
    audio_tmp_file: _TemporaryFileWrapper[bytes],
):
    media_tmp_file.flush()

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        media_tmp_file.name,
        "-vn",
        "-c:a",
        "copy",
        audio_tmp_file.name,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

    audio_tmp_file.seek(0)
