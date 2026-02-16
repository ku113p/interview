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
    ActiveInterviewContextManager,
    LeafCoverageManager,
    LeafHistoryManager,
)

# Knowledge Managers
from .knowledge_managers import (
    UserKnowledgeAreasManager,
    UserKnowledgeManager,
)
from .models import (
    ActiveInterviewContext,
    History,
    LeafCoverage,
    LifeArea,
    User,
    UserKnowledge,
    UserKnowledgeArea,
)

__all__ = [
    # Models
    "ActiveInterviewContext",
    "History",
    "LeafCoverage",
    "LifeArea",
    "User",
    "UserKnowledge",
    "UserKnowledgeArea",
    # Managers
    "ActiveInterviewContextManager",
    "HistoriesManager",
    "LeafCoverageManager",
    "LeafHistoryManager",
    "LifeAreasManager",
    "UserKnowledgeAreasManager",
    "UserKnowledgeManager",
    "UsersManager",
]
