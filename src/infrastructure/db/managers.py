"""Database managers facade - re-exports all database models and managers.

This module provides a single import point for all database entities.
"""

# Domain Models
# Area Data Managers
from .area_data_managers import (
    AreaSummariesManager,
    LifeAreaMessagesManager,
)

# Core Managers
from .core_managers import (
    HistoriesManager,
    LifeAreasManager,
    UsersManager,
)

# Knowledge Managers
from .knowledge_managers import (
    UserKnowledgeAreasManager,
    UserKnowledgeManager,
)
from .models import (
    AreaSummary,
    History,
    LifeArea,
    LifeAreaMessage,
    User,
    UserKnowledge,
    UserKnowledgeArea,
)

__all__ = [
    # Models
    "AreaSummary",
    "History",
    "LifeArea",
    "LifeAreaMessage",
    "User",
    "UserKnowledge",
    "UserKnowledgeArea",
    # Managers
    "AreaSummariesManager",
    "HistoriesManager",
    "LifeAreasManager",
    "LifeAreaMessagesManager",
    "UserKnowledgeAreasManager",
    "UserKnowledgeManager",
    "UsersManager",
]
