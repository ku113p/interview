import asyncio
import io
import shutil
from typing import BinaryIO

from pydantic import BaseModel, ConfigDict

from src.domain import message


def check_ffmpeg_availability():
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg not found. Please install it:\n"
            "  macOS: brew install ffmpeg\n"
            "  Ubuntu/Debian: apt-get install ffmpeg\n"
            "  Or visit: https://ffmpeg.org/download.html"
        )


class State(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    message: message.MediaMessage
    media_file: BinaryIO | None = None
    audio_file: BinaryIO | None = None


async def extract_audio(state: State):
    c_msg = state.message
    m_file = state.media_file
    audio_file = state.audio_file
    assert m_file is not None and audio_file is not None

    await write_file(m_file, c_msg.content)
    await extract_audio_to_wav(m_file, audio_file)
    return {"audio_file": audio_file}


async def write_file(tmp_file: BinaryIO | None, stream: io.BytesIO):
    assert tmp_file is not None
    tmp_file.seek(0)
    tmp_file.write(stream.read())
    tmp_file.seek(0)
    return tmp_file


async def extract_audio_to_wav(
    media_tmp_file: BinaryIO | None, audio_tmp_file: BinaryIO | None
):
    assert media_tmp_file is not None and audio_tmp_file is not None
    media_tmp_file.flush()

    cmd = [
        "ffmpeg",
        "-y",  # Overwrite without prompt
        "-i",
        media_tmp_file.name,
        "-vn",  # No video
        "-ac",
        "1",  # Mono audio
        "-ar",
        "16000",  # 16kHz sample rate (speech recognition standard)
        "-c:a",
        "pcm_s16le",  # 16-bit PCM codec
        audio_tmp_file.name,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

    audio_tmp_file.seek(0)
