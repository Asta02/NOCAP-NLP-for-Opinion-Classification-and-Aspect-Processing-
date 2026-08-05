"""
=========================================================
Review Repository
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Repository for ReviewModel persistence.
"""

from __future__ import annotations

from sqlalchemy import (
    select,
)

from sqlalchemy.orm import (
    Session,
)

from analysis.schemas import (
    ReviewAnalysis,
)

from database.models.review import (
    ReviewModel,
)

from database.models.review_aspect import (
    ReviewAspectModel,
)

from database.models.review_keyword import (
    ReviewKeywordModel,
)

from database.models.review_recommendation import (
    ReviewRecommendationModel,
)

from database.repositories.base_repository import (
    BaseRepository,
)


class ReviewRepository(
    BaseRepository[ReviewModel],
):
    """
    Repository for ReviewModel.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:

        super().__init__(
            session=session,
            model=ReviewModel,
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        analysis: ReviewAnalysis,
        *,
        company_id: int,
        upload_id: int,
        review_text: str,
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
    ) -> ReviewModel:
        """
        Persist a review analysis.
        """

        review = ReviewModel(

            company_id=company_id,
            upload_id=upload_id,

            review_date=review_date,
            employment_status=employment_status,

            job_title=job_title,
            summary=summary,

            # Store the original review text from the CSV,
            # not the merged NLP analysis text.
            review_text=review_text,

            overall_rating=overall_rating,
            work_life_balance=work_life_balance,
            culture_values=culture_values,
            career_opportunities=career_opportunities,
            compensation_benefits=compensation_benefits,
            senior_management=senior_management,

            sentiment_label=analysis.sentiment.label,
            sentiment_label_id=analysis.sentiment.label_id,
            sentiment_confidence=analysis.sentiment.confidence,
            sentiment_model_version=analysis.sentiment.model_version,

            topic_id=(
                analysis.topic.topic_id
                if analysis.topic
                else None
            ),

            topic_name=(
                analysis.topic.topic_name
                if analysis.topic
                else None
            ),

            topic_probability=(
                analysis.topic.probability
                if analysis.topic
                else None
            ),

            topic_model_version=(
                analysis.topic.model_version
                if analysis.topic
                else None
            ),

            processing_time_ms=analysis.processing_time_ms,

        )

        self.session.add(
            review,
        )

        #
        # Generate review.id without committing.
        #
        self.session.flush()

        # =================================================
        # ASPECTS
        # =================================================

        for aspect in analysis.aspects:

            self.session.add(

                ReviewAspectModel(

                    review_id=review.id,

                    aspect=aspect.aspect,

                    phrase=aspect.phrase,

                    sentiment_label=(
                        aspect.prediction.label
                    ),

                    sentiment_label_id=(
                        aspect.prediction.label_id
                    ),

                    sentiment_confidence=(
                        aspect.prediction.confidence
                    ),

                    sentiment_model_version=(
                        aspect.prediction.model_version
                    ),

                )

            )

        # =================================================
        # KEYWORDS
        # =================================================

        for keyword in analysis.keywords:

            self.session.add(

                ReviewKeywordModel(

                    review_id=review.id,

                    keyword=keyword.keyword,

                    score=keyword.score,

                )

            )

        # =================================================
        # RECOMMENDATIONS
        # =================================================

        if analysis.recommendation is not None:

            self.session.add(

                ReviewRecommendationModel(

                    review_id=review.id,

                    category="General",

                    priority="MEDIUM",

                    recommendation=(
                        analysis.recommendation.text
                    ),

                )

            )

        #
        # Flush related inserts.
        #
        self.session.flush()

        self.session.refresh(
            review,
        )

        return review

    # =====================================================
    # REVIEW-SPECIFIC QUERIES
    # =====================================================

    def list_by_company(
        self,
        company_id: int,
    ) -> list[ReviewModel]:
        """
        List all reviews for a company.
        """

        statement = (

            select(
                ReviewModel,
            )

            .where(
                ReviewModel.company_id == company_id,
            )

            .order_by(
                ReviewModel.created_at.desc(),
            )

        )

        return list(

            self.session.scalars(
                statement,
            )

        )

    def list_by_upload(
        self,
        upload_id: int,
    ) -> list[ReviewModel]:
        """
        List all reviews from an upload.
        """

        statement = (

            select(
                ReviewModel,
            )

            .where(
                ReviewModel.upload_id == upload_id,
            )

            .order_by(
                ReviewModel.created_at.desc(),
            )

        )

        return list(

            self.session.scalars(
                statement,
            )

        )

    def list_by_topic(
        self,
        topic_name: str,
    ) -> list[ReviewModel]:
        """
        List reviews by topic.
        """

        statement = (

            select(
                ReviewModel,
            )

            .where(
                ReviewModel.topic_name == topic_name,
            )

            .order_by(
                ReviewModel.created_at.desc(),
            )

        )

        return list(

            self.session.scalars(
                statement,
            )

        )

    def list_by_sentiment(
        self,
        sentiment_label: str,
    ) -> list[ReviewModel]:
        """
        List reviews by sentiment.
        """

        statement = (

            select(
                ReviewModel,
            )

            .where(
                ReviewModel.sentiment_label == sentiment_label,
            )

            .order_by(
                ReviewModel.created_at.desc(),
            )

        )

        return list(

            self.session.scalars(
                statement,
            )

        )