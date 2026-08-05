"""
=========================================================
Analytics Repository
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Repository providing aggregated analytics
queries for dashboards and reporting.
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

from database.models.review import (
    ReviewModel,
)

from database.models.review_aspect import (
    ReviewAspectModel,
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
    # OVERVIEW
    # =====================================================

    def dashboard_overview(
        self,
    ) -> dict[str, int]:

        return {

            "companies": (
                self.session.scalar(
                    select(
                        func.count(),
                    ).select_from(
                        CompanyModel,
                    )
                )
                or 0
            ),

            "uploads": (
                self.session.scalar(
                    select(
                        func.count(),
                    ).select_from(
                        UploadModel,
                    )
                )
                or 0
            ),

            "reviews": (
                self.session.scalar(
                    select(
                        func.count(),
                    ).select_from(
                        ReviewModel,
                    )
                )
                or 0
            ),

        }

    # =====================================================
    # SENTIMENT
    # =====================================================

    def sentiment_distribution(
        self,
    ) -> list[dict[str, object]]:

        statement = (

            select(

                ReviewModel.sentiment_label,

                func.count(),

            )

            .group_by(
                ReviewModel.sentiment_label,
            )

            .order_by(
                func.count().desc(),
            )

        )

        return [

            {

                "label": label,

                "count": count,

            }

            for label, count in (
                self.session.execute(
                    statement,
                )
            )

        ]

    # =====================================================
    # TOPICS
    # =====================================================

    def topic_distribution(
        self,
    ) -> list[dict[str, object]]:

        statement = (

            select(

                ReviewModel.topic_name,

                func.count(),

            )

            .group_by(
                ReviewModel.topic_name,
            )

            .order_by(
                func.count().desc(),
            )

        )

        return [

            {

                "topic": topic,

                "count": count,

            }

            for topic, count in (
                self.session.execute(
                    statement,
                )
            )

        ]

    # =====================================================
    # ASPECTS
    # =====================================================

    def aspect_distribution(
        self,
    ) -> list[dict[str, object]]:

        statement = (

            select(

                ReviewAspectModel.aspect,

                func.count(),

            )

            .group_by(
                ReviewAspectModel.aspect,
            )

            .order_by(
                func.count().desc(),
            )

        )

        return [

            {

                "aspect": aspect,

                "count": count,

            }

            for aspect, count in (
                self.session.execute(
                    statement,
                )
            )

        ]

    # =====================================================
    # COMPANY
    # =====================================================

    def reviews_per_company(
        self,
    ) -> list[dict[str, object]]:

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

                "company": company,

                "reviews": reviews,

            }

            for company, reviews in (
                self.session.execute(
                    statement,
                )
            )

        ]

    # =====================================================
    # MONTHLY
    # =====================================================

    def monthly_reviews(
        self,
    ) -> list[dict[str, object]]:

        statement = (

            select(

                func.date_trunc(

                    "month",

                    ReviewModel.created_at,

                ),

                func.count(),

            )

            .group_by(

                func.date_trunc(

                    "month",

                    ReviewModel.created_at,

                )

            )

            .order_by(

                func.date_trunc(

                    "month",

                    ReviewModel.created_at,

                )

            )

        )

        return [

            {
                "month": month,
                "count": count,
            }

            for month, count in (
                self.session.execute(
                    statement,
                )
            )

        ]