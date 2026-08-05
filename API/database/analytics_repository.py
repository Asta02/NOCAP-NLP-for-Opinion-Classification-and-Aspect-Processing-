"""
=========================================================
Analytics Repository
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Repository providing aggregated statistics
for dashboards and analytics.
"""

from __future__ import annotations

from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import (
    Session,
)

from database.models.company import (
    CompanyModel,
)

from database.models.processing_job import (
    ProcessingJobModel,
)

from database.models.review import (
    ReviewModel,
)

from database.models.review_keyword import (
    ReviewKeywordModel,
)

from database.models.upload import (
    UploadModel,
)


class AnalyticsRepository:
    """
    Repository for dashboard analytics.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:

        self.session = session

    # =====================================================
    # COMPANY DASHBOARD
    # =====================================================
    def overview(
        self,
        company_id: int,
    ) -> dict:

        total_reviews = self.session.scalar(

            select(
                func.count(
                    ReviewModel.id,
                )
            )

            .where(
                ReviewModel.company_id == company_id,
            )

        ) or 0

        average_rating = self.session.scalar(

            select(
                func.avg(
                    ReviewModel.overall_rating,
                )
            )

            .where(
                ReviewModel.company_id == company_id,
            )

        ) or 0.0

        positive = self.session.scalar(

            select(
                func.count(
                    ReviewModel.id,
                )
            )

            .where(
                ReviewModel.company_id == company_id,
                ReviewModel.sentiment_label == "Positive",
            )

        ) or 0

        neutral = self.session.scalar(

            select(
                func.count(
                    ReviewModel.id,
                )
            )

            .where(
                ReviewModel.company_id == company_id,
                ReviewModel.sentiment_label == "Neutral",
            )

        ) or 0

        negative = self.session.scalar(

            select(
                func.count(
                    ReviewModel.id,
                )
            )

            .where(
                ReviewModel.company_id == company_id,
                ReviewModel.sentiment_label == "Negative",
            )

        ) or 0

        return {

            "total_reviews": total_reviews,

            "average_rating": round(
                float(
                    average_rating,
                ),
                2,
            ),

            "positive_reviews": positive,

            "neutral_reviews": neutral,

            "negative_reviews": negative,

        }

    def employee_mood(
        self,
        company_id: int,
    ) -> dict:

        overview = self.overview(
            company_id,
        )

        total = max(
            overview["total_reviews"],
            1,
        )

        return {

            "positive": round(
                overview["positive_reviews"] * 100 / total,
            ),

            "neutral": round(
                overview["neutral_reviews"] * 100 / total,
            ),

            "negative": round(
                overview["negative_reviews"] * 100 / total,
            ),

        }

    def monthly_sentiment(
        self,
        company_id: int,
    ) -> list[dict]:
        """
        Return monthly sentiment counts.
        """

        month = func.date_trunc(
            "month",
            ReviewModel.created_at,
        )

        statement = (

            select(

                month.label("month"),

                ReviewModel.sentiment_label,

                func.count(),

            )

            .where(
                ReviewModel.company_id == company_id,
            )

            .group_by(
                month,
                ReviewModel.sentiment_label,
            )

            .order_by(
                month,
            )

        )

        return [

            {

                "month": row[0],

                "sentiment": row[1],

                "count": row[2],

            }

            for row in self.session.execute(
                statement,
            )

        ]

    def rating_distribution(
        self,
        company_id: int,
    ) -> list[dict]:

        statement = (

            select(

                ReviewModel.overall_rating,

                func.count(),

            )

            .where(
                ReviewModel.company_id == company_id,
            )

            .group_by(
                ReviewModel.overall_rating,
            )

            .order_by(
                ReviewModel.overall_rating,
            )

        )

        return [

            {

                "rating": row[0],

                "count": row[1],

            }

            for row in self.session.execute(
                statement,
            )

        ]

    def top_topics(
        self,
        company_id: int,
        limit: int = 10,
    ) -> list[dict]:

        statement = (

            select(

                ReviewModel.topic_name,

                func.count(),

            )

            .where(
                ReviewModel.company_id == company_id,
            )

            .group_by(
                ReviewModel.topic_name,
            )

            .order_by(
                func.count().desc(),
            )

            .limit(
                limit,
            )

        )

        return [

            {

                "topic": row[0],

                "count": row[1],

            }

            for row in self.session.execute(
                statement,
            )

        ]

    def top_keywords(
        self,
        company_id: int,
        limit: int = 10,
    ) -> list[dict]:

        statement = (

            select(

                ReviewKeywordModel.keyword,

                func.avg(
                    ReviewKeywordModel.score,
                ),

            )

            .join(
                ReviewModel,
            )

            .where(
                ReviewModel.company_id == company_id,
            )

            .group_by(
                ReviewKeywordModel.keyword,
            )

            .order_by(
                func.avg(
                    ReviewKeywordModel.score,
                ).desc(),
            )

            .limit(
                limit,
            )

        )

        return [

            {

                "keyword": row[0],

                "score": float(
                    row[1],
                ),

            }

            for row in self.session.execute(
                statement,
            )

        ]

    def recent_reviews(
        self,
        company_id: int,
        limit: int = 5,
    ):

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

            .limit(
                limit,
            )

        )

        return list(

            self.session.scalars(
                statement,
            )

        )

    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    def monthly_imports(
        self,
    ) -> list[dict]:
        """
        Return uploads grouped by month.
        """

        month = func.date_trunc(
            "month",
            UploadModel.uploaded_at,
        )

        statement = (

            select(

                month.label("month"),

                func.count(),

            )

            .group_by(
                month,
            )

            .order_by(
                month,
            )

        )

        return [

            {

                "month": row[0],

                "count": row[1],

            }

            for row in self.session.execute(
                statement,
            )

        ]

    def processing_status(
        self,
    ) -> list[dict]:
        """
        Return processing job counts by status.
        """

        statement = (

            select(

                ProcessingJobModel.status,

                func.count(),

            )

            .group_by(
                ProcessingJobModel.status,
            )

            .order_by(
                ProcessingJobModel.status,
            )

        )

        return [

            {

                "status": (
                    row[0].value
                    if hasattr(
                        row[0],
                        "value",
                    )
                    else row[0]
                ),

                "count": row[1],

            }

            for row in self.session.execute(
                statement,
            )

        ]

    def total_companies(
        self,
    ) -> int:

        return self.session.scalar(

            select(
                func.count(
                    CompanyModel.id,
                )
            )

        ) or 0

    def total_reviews(
        self,
    ) -> int:

        return self.session.scalar(

            select(
                func.count(
                    ReviewModel.id,
                )
            )

        ) or 0

    def pending_jobs(
        self,
    ) -> int:

        return self.session.scalar(

            select(
                func.count(
                    ProcessingJobModel.id,
                )
            )

            .where(
                ProcessingJobModel.status != "COMPLETED",
            )

        ) or 0

    def reviews_per_company(
        self,
    ) -> list[dict]:

        statement = (

            select(

                CompanyModel.company_name,

                func.count(
                    ReviewModel.id,
                ),

            )

            .join(
                ReviewModel,
            )

            .group_by(
                CompanyModel.company_name,
            )

            .order_by(
                func.count(
                    ReviewModel.id,
                ).desc(),
            )

        )

        return [

            {

                "company_name": row[0],

                "count": row[1],

            }

            for row in self.session.execute(
                statement,
            )

        ]

    def latest_uploads(
        self,
        limit: int = 10,
    ):

        statement = (

            select(
                UploadModel,
            )

            .order_by(
                UploadModel.uploaded_at.desc(),
            )

            .limit(
                limit,
            )

        )

        return list(

            self.session.scalars(
                statement,
            )

        )