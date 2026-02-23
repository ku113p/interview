"""MCP server tool definitions (read-only)."""

import uuid

from fastmcp import FastMCP

from src.infrastructure.db import managers as db
from src.infrastructure.embeddings import get_embedding_client
from src.shared.similarity import find_top_k

from .auth import AuthMiddleware, get_user_id

mcp = FastMCP("Interview Assistant", middleware=[AuthMiddleware()])


def _summary_to_dict(s: db.Summary) -> dict:
    return {
        "id": str(s.id),
        "area_id": str(s.area_id),
        "summary_text": s.summary_text,
        "created_at": s.created_at,
    }


def _area_to_dict(a: db.LifeArea) -> dict:
    return {
        "id": str(a.id),
        "title": a.title,
        "parent_id": str(a.parent_id) if a.parent_id else None,
        "covered_at": a.covered_at,
    }


def _knowledge_to_dict(k: db.UserKnowledge) -> dict:
    return {
        "id": str(k.id),
        "description": k.description,
        "kind": k.kind,
        "confidence": k.confidence,
    }


async def _embed_query(query: str) -> list[float]:
    client = get_embedding_client()
    return await client.aembed_query(query)


@mcp.tool
async def search_summaries(query: str, limit: int = 5) -> list[dict]:
    """Search summaries by semantic similarity to a query string."""
    limit = max(1, min(limit, 100))
    user_id = get_user_id()
    candidates = await db.SummariesManager.list_vectors_by_user(user_id)
    if not candidates:
        return []
    query_vec = await _embed_query(query)
    top = find_top_k(query_vec, candidates, k=limit)
    top_ids = [uuid.UUID(sid) for sid, _ in top]
    full_records = await db.SummariesManager.get_by_ids(top_ids)
    by_id = {str(s.id): s for s in full_records}
    return [
        {**_summary_to_dict(by_id[sid]), "score": round(score, 4)}
        for sid, score in top
        if sid in by_id
    ]


@mcp.tool
async def get_summaries(area_id: str | None = None) -> list[dict]:
    """Get all summaries, optionally filtered by area_id."""
    user_id = get_user_id()
    if area_id is not None:
        try:
            parsed = uuid.UUID(area_id)
        except ValueError:
            return []
        area = await db.LifeAreasManager.get_by_id(parsed)
        if area is None or area.user_id != user_id:
            return []
        items = await db.SummariesManager.list_by_area(parsed)
    else:
        items = await db.SummariesManager.list_by_user(user_id)
    return [_summary_to_dict(s) for s in items]


@mcp.tool
async def get_knowledge(kind: str | None = None) -> list[dict]:
    """Get knowledge items, optionally filtered by kind ('skill' or 'fact')."""
    user_id = get_user_id()
    items = await db.UserKnowledgeManager.list_by_user(user_id)
    if kind is not None:
        items = [k for k in items if k.kind == kind]
    return [_knowledge_to_dict(k) for k in items]


@mcp.tool
async def get_areas() -> list[dict]:
    """Get flat list of all life areas for the authenticated user."""
    user_id = get_user_id()
    areas = await db.LifeAreasManager.list_by_user(user_id)
    return [_area_to_dict(a) for a in areas]
