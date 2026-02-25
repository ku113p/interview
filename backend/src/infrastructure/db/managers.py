"""Database managers facade - re-exports all database models and managers.

This module provides a single import point for all database entities.
"""

# API Key Managers
from .api_managers import ApiKeysManager

# Core Managers
from .core_managers import (
    HistoriesManager,
    LifeAreasManager,
    UsersManager,
)

# Interview Managers
from .interview_managers import (
    LeafHistoryManager,
    SummariesManager,
)

# Knowledge Managers
from .knowledge_managers import (
    UserKnowledgeManager,
)
from .models import (
    ApiKey,
    History,
    LifeArea,
    Summary,
    User,
    UserKnowledge,
)

__all__ = [
    # Models
    "ApiKey",
    "History",
    "LifeArea",
    "Summary",
    "User",
    "UserKnowledge",
    # Managers
    "ApiKeysManager",
    "HistoriesManager",
    "LeafHistoryManager",
    "LifeAreasManager",
    "SummariesManager",
    "UserKnowledgeManager",
    "UsersManager",
]
