"""
=========================================================
Application Startup
=========================================================

Description
-----------
Validate application dependencies during startup.
"""

from __future__ import annotations

from analysis.review_analyzer import (
    ReviewAnalyzer,
)

from database.unit_of_work import (
    UnitOfWork,
)


def startup() -> None:
    """
    Validate that core components are ready.
    """

    print("=" * 60)
    print("Application Startup")
    print("=" * 60)

    # Load NLP models
    analyzer = ReviewAnalyzer()
    analyzer.health()

    # Validate database connection
    with UnitOfWork() as uow:
        uow.reviews.count()

    print("✓ NLP models loaded")
    print("✓ Database connected")
    print("=" * 60)