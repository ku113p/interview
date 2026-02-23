"""Unit tests for ApiKeysManager."""

import time

import pytest
from src.infrastructure.db import managers as db
from src.infrastructure.db.api_managers import hash_key
from src.shared.ids import new_id


class TestApiKeysManager:
    """Tests for ApiKeysManager with hashed keys."""

    @pytest.mark.asyncio
    async def test_create_and_get_by_key(self, temp_db, sample_user):
        """Round-trip: create with hash, look up by raw key."""
        raw_key = "abcdef1234567890abcdef1234567890"
        api_key = db.ApiKey(
            id=new_id(),
            key_hash=hash_key(raw_key),
            key_prefix=raw_key[:8],
            user_id=sample_user.id,
            label="test-key",
            created_at=time.time(),
        )
        await db.ApiKeysManager.create(api_key.id, api_key)

        result = await db.ApiKeysManager.get_by_key(raw_key)
        assert result is not None
        assert result.id == api_key.id
        assert result.key_prefix == "abcdef12"
        assert result.label == "test-key"

    @pytest.mark.asyncio
    async def test_get_by_key_not_found(self, temp_db):
        """Lookup of non-existent key should return None."""
        result = await db.ApiKeysManager.get_by_key("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_by_user(self, temp_db, sample_user):
        """Should list only keys belonging to the user."""
        other_user_id = new_id()
        now = time.time()

        for i, uid in enumerate([sample_user.id, sample_user.id, other_user_id]):
            key = db.ApiKey(
                id=new_id(),
                key_hash=hash_key(f"key{i}"),
                key_prefix=f"key{i}xxxx"[:8],
                user_id=uid,
                label=f"label-{i}",
                created_at=now + i,
            )
            await db.ApiKeysManager.create(key.id, key)

        results = await db.ApiKeysManager.list_by_user(sample_user.id)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_delete(self, temp_db, sample_user):
        """Key should be gone after deletion."""
        raw_key = "deleteme1234567890abcdef12345678"
        api_key = db.ApiKey(
            id=new_id(),
            key_hash=hash_key(raw_key),
            key_prefix=raw_key[:8],
            user_id=sample_user.id,
            label="to-delete",
            created_at=time.time(),
        )
        await db.ApiKeysManager.create(api_key.id, api_key)
        await db.ApiKeysManager.delete(api_key.id)

        result = await db.ApiKeysManager.get_by_key(raw_key)
        assert result is None

    def test_hash_key_deterministic(self):
        """SHA-256 hash should be consistent across calls."""
        key = "test-key-value"
        assert hash_key(key) == hash_key(key)
        assert len(hash_key(key)) == 64  # hex digest length
