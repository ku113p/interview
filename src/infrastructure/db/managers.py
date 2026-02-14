"""Database managers facade - re-exports all database models and managers.

This module provides a single import point for all database entities.
"""

# Area Data Managers
from .area_data_managers import AreaSummariesManager

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
    AreaSummary,
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
    "AreaSummary",
    "History",
    "LeafCoverage",
    "LifeArea",
    "User",
    "UserKnowledge",
    "UserKnowledgeArea",
    # Managers
    "ActiveInterviewContextManager",
    "AreaSummariesManager",
    "HistoriesManager",
    "LeafCoverageManager",
    "LeafHistoryManager",
    "LifeAreasManager",
    "UserKnowledgeAreasManager",
    "UserKnowledgeManager",
    "UsersManager",
]
