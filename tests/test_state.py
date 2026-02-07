"""Unit tests for State model file handling."""

import tempfile
from pathlib import Path

from langchain_core.messages import HumanMessage
from src.application.state import State, Target
from src.domain import ClientMessage, InputMode, User
from src.shared.ids import new_id


class TestStateFileHandling:
    """Test State model accepts file paths as strings."""

    def test_state_accepts_string_file_paths(self):
        """State should accept file paths as strings for media_file and audio_file."""
        # Arrange
        user = User(id=new_id(), mode=InputMode.auto)
        message = ClientMessage(data="test message")
        media_path = "/tmp/test_media.mp4"
        audio_path = "/tmp/test_audio.wav"

        # Act
        state = State(
            user=user,
            message=message,
            media_file=media_path,
            audio_file=audio_path,
            text="test",
            target=Target.interview,
            messages=[],
            messages_to_save={},
            success=None,
            area_id=new_id(),
            was_covered=False,
        )

        # Assert
        assert state.media_file == media_path
        assert state.audio_file == audio_path
        assert isinstance(state.media_file, str)
        assert isinstance(state.audio_file, str)

    def test_state_accepts_none_files(self):
        """State should accept None values for media_file and audio_file."""
        # Arrange
        user = User(id=new_id(), mode=InputMode.auto)
        message = ClientMessage(data="test message")

        # Act
        state = State(
            user=user,
            message=message,
            media_file=None,
            audio_file=None,
            text="test",
            target=Target.interview,
            messages=[],
            messages_to_save={},
            success=None,
            area_id=new_id(),
            was_covered=False,
        )

        # Assert
        assert state.media_file is None
        assert state.audio_file is None

    def test_state_with_actual_tempfile_paths(self):
        """State should work with actual temporary file paths."""
        # Arrange
        user = User(id=new_id(), mode=InputMode.auto)
        message = ClientMessage(data="test message")

        with tempfile.NamedTemporaryFile(delete=False) as media_tmp:
            media_path = media_tmp.name
        with tempfile.NamedTemporaryFile(delete=False) as audio_tmp:
            audio_path = audio_tmp.name

        try:
            # Act
            state = State(
                user=user,
                message=message,
                media_file=media_path,
                audio_file=audio_path,
                text="test",
                target=Target.interview,
                messages=[],
                messages_to_save={},
                success=None,
                area_id=new_id(),
                was_covered=False,
            )

            # Assert
            assert state.media_file == media_path
            assert state.audio_file == audio_path
            assert Path(state.media_file).exists()
            assert Path(state.audio_file).exists()
        finally:
            # Cleanup
            Path(media_path).unlink(missing_ok=True)
            Path(audio_path).unlink(missing_ok=True)

    def test_state_maintains_file_paths_through_updates(self):
        """State should maintain file paths when updated."""
        # Arrange
        user = User(id=new_id(), mode=InputMode.auto)
        message = ClientMessage(data="test message")
        media_path = "/tmp/test_media.mp4"
        audio_path = "/tmp/test_audio.wav"

        state = State(
            user=user,
            message=message,
            media_file=media_path,
            audio_file=audio_path,
            text="test",
            target=Target.interview,
            messages=[],
            messages_to_save={},
            success=None,
            area_id=new_id(),
            was_covered=False,
        )

        # Act - Add a message to state
        new_message = HumanMessage(content="Hello")
        updated_state = state.model_copy(
            update={"messages": [new_message], "text": "updated"}
        )

        # Assert
        assert updated_state.media_file == media_path
        assert updated_state.audio_file == audio_path
        assert updated_state.text == "updated"
        assert len(updated_state.messages) == 1
