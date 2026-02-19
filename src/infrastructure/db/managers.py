"""Database managers facade - re-exports all database models and managers.

This module provides a single import point for all database entities.
"""

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
    History,
    LifeArea,
    Summary,
    User,
    UserKnowledge,
)

__all__ = [
    # Models
    "History",
    "LifeArea",
    "Summary",
    "User",
    "UserKnowledge",
    # Managers
    "HistoriesManager",
    "LeafHistoryManager",
    "LifeAreasManager",
    "SummariesManager",
    "UserKnowledgeManager",
    "UsersManager",
]
