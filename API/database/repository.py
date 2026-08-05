"""
=========================================================
Review Repository
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Repository for persisting review analysis
results into PostgreSQL.
"""

from __future__ import annotations

from sqlalchemy import (
    delete,
    func,
    select,
)

from sqlalchemy.orm import (
    Session,
    selectinload,
)

from analysis.schemas import (
    ReviewAnalysis,
)

from .models import (
    AspectModel,
    ReviewModel,
)


class ReviewRepository:
    """
    Repository for ReviewAnalysis.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:

        self.session = session

    # =====================================================
    # CREATE
    # =====================================================

    def save(
        self,
        analysis: ReviewAnalysis,
    ) -> ReviewModel:
        """
        Persist one review analysis.
        """

        review = ReviewModel(

            review_text=analysis.text,

            sentiment_label=(
                analysis.sentiment.label
            ),

            sentiment_label_id=(
                analysis.sentiment.label_id
            ),

            sentiment_confidence=(
                analysis.sentiment.confidence
            ),

            sentiment_model_version=(
                analysis.sentiment.model_version
            ),

            topic_id=(
                analysis.topic.topic_id
            ),

            topic_name=(
                analysis.topic.topic_name
            ),

            topic_probability=(
                analysis.topic.probability
            ),

            topic_keywords=(
                analysis.topic.keywords
            ),

            topic_model_version=(
                analysis.topic.model_version
            ),

            processing_time_ms=(
                analysis.processing_time_ms
            ),

        )

        for aspect in analysis.aspects:

            review.aspects.append(

                AspectModel(

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

        self.session.add(
            review
        )

        #
        # Flush instead of commit so the ID is generated.
        # UnitOfWork will commit the transaction.
        #
        self.session.flush()

        self.session.refresh(
            review
        )

        return review

    # =====================================================
    # READ
    # =====================================================

    def get(
        self,
        review_id: int,
    ) -> ReviewModel | None:
        """
        Return one review.
        """

        statement = (

            select(
                ReviewModel
            )

            .options(
                selectinload(
                    ReviewModel.aspects
                )
            )

            .where(
                ReviewModel.id == review_id
            )

        )

        return self.session.scalar(
            statement
        )

    def list(
        self,
    ) -> list[ReviewModel]:
        """
        Return all reviews.
        """

        statement = (

            select(
                ReviewModel
            )

            .options(
                selectinload(
                    ReviewModel.aspects
                )
            )

            .order_by(
                ReviewModel.created_at.desc()
            )

        )

        return list(

            self.session.scalars(
                statement
            )

        )

    def count(
        self,
    ) -> int:
        """
        Return total number of reviews.
        """

        statement = select(
            func.count(
                ReviewModel.id
            )
        )

        return (

            self.session.scalar(
                statement
            )

            or 0

        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        review_id: int,
    ) -> bool:
        """
        Delete one review.
        """

        result = self.session.execute(

            delete(
                ReviewModel
            ).where(
                ReviewModel.id == review_id
            )

        )

        return result.rowcount > 0