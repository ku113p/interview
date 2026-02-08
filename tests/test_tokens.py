"""Tests for token estimation and context management utilities."""

from langchain_core.messages import AIMessage, HumanMessage
from src.shared.tokens import (
    CHARS_PER_TOKEN,
    estimate_message_tokens,
    estimate_tokens,
    trim_messages_to_budget,
)


class TestEstimateTokens:
    """Tests for estimate_tokens function."""

    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_short_string(self):
        # "hi" = 2 chars, 2 // 4 = 0
        assert estimate_tokens("hi") == 0

    def test_exact_token_boundary(self):
        # 4 chars = 1 token
        assert estimate_tokens("abcd") == 1

    def test_multiple_tokens(self):
        # 20 chars = 5 tokens
        assert estimate_tokens("a" * 20) == 5

    def test_uses_chars_per_token_constant(self):
        text = "a" * CHARS_PER_TOKEN
        assert estimate_tokens(text) == 1


class TestEstimateMessageTokens:
    """Tests for estimate_message_tokens function."""

    def test_human_message(self):
        msg = HumanMessage(content="Hello world!")  # 12 chars = 3 tokens
        assert estimate_message_tokens(msg) == 3

    def test_ai_message(self):
        msg = AIMessage(content="Response here")  # 13 chars = 3 tokens
        assert estimate_message_tokens(msg) == 3

    def test_empty_message(self):
        msg = HumanMessage(content="")
        assert estimate_message_tokens(msg) == 0

    def test_long_message(self):
        msg = HumanMessage(content="a" * 400)  # 400 chars = 100 tokens
        assert estimate_message_tokens(msg) == 100


class TestTrimMessagesToBudget:
    """Tests for trim_messages_to_budget function."""

    def test_empty_list(self):
        result = trim_messages_to_budget([], 1000)
        assert result == []

    def test_within_budget_returns_all(self):
        messages = [
            HumanMessage(content="Hi"),
            AIMessage(content="Hello"),
        ]
        result = trim_messages_to_budget(messages, 1000)
        assert len(result) == 2
        assert result == messages

    def test_trims_oldest_messages(self):
        messages = [
            HumanMessage(content="a" * 40),  # 10 tokens
            AIMessage(content="b" * 40),  # 10 tokens
            HumanMessage(content="c" * 40),  # 10 tokens
        ]
        # Budget of 15 tokens should keep only last 1 message
        result = trim_messages_to_budget(messages, 15)
        assert len(result) == 1
        assert result[0].content == "c" * 40

    def test_keeps_most_recent(self):
        messages = [
            HumanMessage(content="a" * 40),  # 10 tokens
            AIMessage(content="b" * 40),  # 10 tokens
            HumanMessage(content="c" * 40),  # 10 tokens
        ]
        result = trim_messages_to_budget(messages, 12)
        assert len(result) == 1
        assert result[0].content == "c" * 40

    def test_always_keeps_last_message_even_if_over_budget(self):
        messages = [
            HumanMessage(content="a" * 100),  # 25 tokens, exceeds budget
        ]
        result = trim_messages_to_budget(messages, 5)
        assert len(result) == 1
        assert result[0] == messages[0]

    def test_preserves_message_order(self):
        messages = [
            HumanMessage(content="a" * 20),  # 5 tokens
            AIMessage(content="b" * 20),  # 5 tokens
            HumanMessage(content="c" * 20),  # 5 tokens
        ]
        # Budget of 12 tokens should keep last 2 messages
        result = trim_messages_to_budget(messages, 12)
        assert len(result) == 2
        assert result[0].content == "b" * 20
        assert result[1].content == "c" * 20

    def test_exact_budget_fit(self):
        messages = [
            HumanMessage(content="a" * 20),  # 5 tokens
            AIMessage(content="b" * 20),  # 5 tokens
        ]
        result = trim_messages_to_budget(messages, 10)
        assert len(result) == 2
