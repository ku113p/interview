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

# Interview Managers
from .interview_managers import (
    ActiveInterviewContextManager,
    LeafCoverageManager,
    LeafExtractionQueueManager,
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
    LeafExtractionQueueItem,
    LifeArea,
    LifeAreaMessage,
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
    "LeafExtractionQueueItem",
    "LifeArea",
    "LifeAreaMessage",
    "User",
    "UserKnowledge",
    "UserKnowledgeArea",
    # Managers
    "ActiveInterviewContextManager",
    "AreaSummariesManager",
    "HistoriesManager",
    "LeafCoverageManager",
    "LeafExtractionQueueManager",
    "LifeAreasManager",
    "LifeAreaMessagesManager",
    "UserKnowledgeAreasManager",
    "UserKnowledgeManager",
    "UsersManager",
]
