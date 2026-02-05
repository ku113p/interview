import asyncio
import io
import shutil

from pydantic import BaseModel, ConfigDict

from src.domain.models import MediaMessage

from ..file_utils import write_file_bytes


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
    message: MediaMessage
    media_file: str
    audio_file: str


async def extract_audio(state: State):
    c_msg = state.message
    m_file = state.media_file
    audio_file = state.audio_file

    await write_file(m_file, c_msg.content)
    await extract_audio_to_wav(m_file, audio_file)
    return {"audio_file": audio_file}


async def write_file(file_path: str, stream: io.BytesIO):
    await write_file_bytes(file_path, stream)
    return file_path


async def extract_audio_to_wav(media_file_path: str, audio_file_path: str):
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite without prompt
        "-i",
        media_file_path,
        "-vn",  # No video
        "-ac",
        "1",  # Mono audio
        "-ar",
        "16000",  # 16kHz sample rate (speech recognition standard)
        "-c:a",
        "pcm_s16le",  # 16-bit PCM codec
        audio_file_path,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")
