"""
=========================================================
Analysis Service
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Application service for review analysis.

Responsibilities
----------------
1. Analyze reviews
2. Persist analysis results
3. Provide retrieval operations

This module MUST NOT

- perform SQL queries directly
- perform HTTP operations
- implement NLP algorithms
"""

from __future__ import annotations

from typing import Sequence

from analysis.review_analyzer import (
    ReviewAnalyzer,
)

from analysis.schemas import (
    ReviewAnalysis,
)

from database.unit_of_work import (
    UnitOfWork,
)


class AnalysisService:
    """
    Application service for review analysis.
    """

    def __init__(
        self,
    ) -> None:

        self.analyzer = ReviewAnalyzer()

    # =================================================
    # ANALYSIS
    # =================================================

    def analyze(
        self,
        review: str,
    ) -> ReviewAnalysis:
        """
        Analyze a single review without persisting.
        """

        return self.analyzer.analyze(
            review,
        )

    def analyze_review(
        self,
        review_text: str,
    ) -> ReviewAnalysis:
        """
        Analyze one review.

        Alias used by the CSV importer.
        """

        return self.analyze(
            review_text,
        )

    def analyze_batch(
        self,
        reviews: Sequence[str],
    ) -> list[ReviewAnalysis]:
        """
        Analyze multiple reviews.
        """

        return [

            self.analyze(
                review,
            )

            for review in reviews

        ]

    # =================================================
    # PERSISTENCE
    # =================================================

    def persist_analysis(
        self,
        analysis: ReviewAnalysis,
        *,
        company_id: int,
        upload_id: int,
        review_date=None,
        employment_status=None,
        job_title: str | None = None,
        summary: str | None = None,
        overall_rating: float | None = None,
        work_life_balance: float | None = None,
        culture_values: float | None = None,
        career_opportunities: float | None = None,
        compensation_benefits: float | None = None,
        senior_management: float | None = None,
    ):
        """
        Persist an analysis result.
        """

        with UnitOfWork() as uow:

            return uow.reviews.create(

                analysis,

                company_id=company_id,

                upload_id=upload_id,

                review_date=review_date,

                employment_status=employment_status,

                job_title=job_title,

                summary=summary,

                overall_rating=overall_rating,

                work_life_balance=work_life_balance,

                culture_values=culture_values,

                career_opportunities=career_opportunities,

                compensation_benefits=compensation_benefits,

                senior_management=senior_management,

            )

    # =================================================
    # DATABASE
    # =================================================

    def list_reviews(
        self,
    ):
        """
        Return all stored reviews.
        """

        with UnitOfWork() as uow:

            return uow.reviews.list()

    def get_review(
        self,
        review_id: int,
    ):
        """
        Return one stored review.
        """

        with UnitOfWork() as uow:

            return uow.reviews.get(
                review_id,
            )

    def delete_review(
        self,
        review_id: int,
    ) -> bool:
        """
        Delete one stored review.
        """

        with UnitOfWork() as uow:

            return uow.reviews.delete(
                review_id,
            )

    def review_count(
        self,
    ) -> int:
        """
        Return total stored reviews.
        """

        with UnitOfWork() as uow:

            return uow.reviews.count()

    # =================================================
    # HEALTH
    # =================================================

    def health(
        self,
    ) -> dict[str, object]:
        """
        Return application health.
        """

        health = self.analyzer.health()

        health[
            "stored_reviews"
        ] = self.review_count()

        return health