"""
=========================================================
Analytics Service
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Application service for analytics.

Responsibilities
----------------
1. Provide aggregated analytics.
2. Coordinate analytics repositories.
3. Prepare dashboard data.
"""

from __future__ import annotations

from database.unit_of_work import (
    UnitOfWork,
)


class AnalyticsService:
    """
    Application service for analytics.
    """

    # =================================================
    # OVERVIEW
    # =================================================

    def dashboard_overview(
        self,
    ) -> dict[str, int]:
        """
        Return dashboard overview.
        """

        with UnitOfWork() as uow:

            return (
                uow.analytics.dashboard_overview()
            )

    # =================================================
    # SENTIMENT
    # =================================================

    def sentiment_distribution(
        self,
    ) -> list[dict[str, object]]:
        """
        Return sentiment distribution.
        """

        with UnitOfWork() as uow:

            return (
                uow.analytics.sentiment_distribution()
            )

    # =================================================
    # TOPICS
    # =================================================

    def topic_distribution(
        self,
    ) -> list[dict[str, object]]:
        """
        Return topic distribution.
        """

        with UnitOfWork() as uow:

            return (
                uow.analytics.topic_distribution()
            )

    # =================================================
    # ASPECTS
    # =================================================

    def aspect_distribution(
        self,
    ) -> list[dict[str, object]]:
        """
        Return aspect distribution.
        """

        with UnitOfWork() as uow:

            return (
                uow.analytics.aspect_distribution()
            )

    # =================================================
    # COMPANIES
    # =================================================

    def reviews_per_company(
        self,
    ) -> list[dict[str, object]]:
        """
        Return review counts per company.
        """

        with UnitOfWork() as uow:

            return (
                uow.analytics.reviews_per_company()
            )

    # =================================================
    # MONTHLY
    # =================================================

    def monthly_reviews(
        self,
    ) -> list[dict[str, object]]:
        """
        Return monthly review counts.
        """

        with UnitOfWork() as uow:

            return (
                uow.analytics.monthly_reviews()
            )

    # =================================================
    # DASHBOARD
    # =================================================

    def dashboard_summary(
        self,
    ) -> dict[str, object]:
        """
        Return complete dashboard summary.
        """

        return {

            "overview": (
                self.dashboard_overview()
            ),

            "sentiment": (
                self.sentiment_distribution()
            ),

            "topics": (
                self.topic_distribution()
            ),

            "aspects": (
                self.aspect_distribution()
            ),

            "companies": (
                self.reviews_per_company()
            ),

            "monthly_reviews": (
                self.monthly_reviews()
            ),

        }