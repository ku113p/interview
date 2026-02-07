"""Unit tests for message bucket utilities."""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.shared.message_buckets import merge_message_buckets


class TestMergeMessageBuckets:
    """Test merge_message_buckets function."""

    def test_merge_empty_buckets(self):
        """Should return empty dict when both inputs are None."""
        result = merge_message_buckets(None, None)
        assert result == {}

    def test_merge_with_left_none(self):
        """Should return right bucket when left is None."""
        msg = HumanMessage(content="hello")
        right = {1000.0: [msg]}

        result = merge_message_buckets(None, right)

        assert result == {1000.0: [msg]}

    def test_merge_with_right_none(self):
        """Should return left bucket when right is None."""
        msg = HumanMessage(content="hello")
        left = {1000.0: [msg]}

        result = merge_message_buckets(left, None)

        assert result == {1000.0: [msg]}

    def test_merge_different_timestamps(self):
        """Should combine messages at different timestamps."""
        msg1 = HumanMessage(content="hello")
        msg2 = AIMessage(content="hi")
        left = {1000.0: [msg1]}
        right = {1001.0: [msg2]}

        result = merge_message_buckets(left, right)

        assert len(result) == 2  # noqa: PLR2004
        assert result[1000.0] == [msg1]
        assert result[1001.0] == [msg2]

    def test_merge_same_timestamp_different_messages(self):
        """Should combine different messages at same timestamp."""
        msg1 = HumanMessage(content="hello")
        msg2 = AIMessage(content="hi")
        left = {1000.0: [msg1]}
        right = {1000.0: [msg2]}

        result = merge_message_buckets(left, right)

        assert len(result[1000.0]) == 2  # noqa: PLR2004
        assert msg1 in result[1000.0]
        assert msg2 in result[1000.0]

    def test_deduplicates_identical_messages(self):
        """Should not duplicate identical messages at same timestamp.

        This tests the key fix: when subgraphs inherit parent state,
        the same message can appear in both parent and child buckets.
        """
        msg = HumanMessage(content="hello")
        left = {1000.0: [msg]}
        right = {1000.0: [msg], 1001.0: [AIMessage(content="hi")]}

        result = merge_message_buckets(left, right)

        # Should have only 1 message at 1000.0, not 2
        assert len(result[1000.0]) == 1
        assert result[1000.0][0].content == "hello"
        # Should still have the AI message at different timestamp
        assert len(result[1001.0]) == 1

    def test_deduplicates_by_type_and_content(self):
        """Should deduplicate based on message type and content."""
        human_msg = HumanMessage(content="test")
        ai_msg = AIMessage(content="test")  # Same content, different type

        left = {1000.0: [human_msg]}
        right = {1000.0: [human_msg, ai_msg]}

        result = merge_message_buckets(left, right)

        # Should have both: same content but different types
        assert len(result[1000.0]) == 2  # noqa: PLR2004
        types = {m.type for m in result[1000.0]}
        assert types == {"human", "ai"}

    def test_preserves_message_order(self):
        """Should preserve order of messages (first occurrence wins)."""
        msg1 = HumanMessage(content="first")
        msg2 = AIMessage(content="second")
        msg3 = HumanMessage(content="third")

        left = {1000.0: [msg1, msg2]}
        right = {1000.0: [msg1, msg3]}  # msg1 is duplicate

        result = merge_message_buckets(left, right)

        assert len(result[1000.0]) == 3  # noqa: PLR2004
        contents = [m.content for m in result[1000.0]]
        assert contents == ["first", "second", "third"]

    def test_handles_tool_messages(self):
        """Should correctly handle ToolMessage types."""
        tool_msg = ToolMessage(content="result", tool_call_id="123")
        ai_msg = AIMessage(content="result")  # Same content, different type

        left = {1000.0: [tool_msg]}
        right = {1000.0: [tool_msg, ai_msg]}

        result = merge_message_buckets(left, right)

        # Should have both: tool and ai messages
        assert len(result[1000.0]) == 2  # noqa: PLR2004
