"""File utilities for handling temporary files in extract flow."""

import io
from pathlib import Path


async def read_file_bytes(file_path: str) -> bytes:
    """Read bytes from a file path.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents as bytes

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    path = Path(file_path)
    return path.read_bytes()


async def write_file_bytes(file_path: str, data: bytes | io.BytesIO) -> None:
    """Write bytes to a file path.

    Args:
        file_path: Path to the file to write
        data: Bytes or BytesIO stream to write

    Raises:
        IOError: If file cannot be written
    """
    path = Path(file_path)
    if isinstance(data, io.BytesIO):
        data.seek(0)
        content = data.read()
    else:
        content = data
    path.write_bytes(content)
