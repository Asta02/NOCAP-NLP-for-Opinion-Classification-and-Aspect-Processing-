"""
=========================================================
Dashboard Service
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Application service providing dashboard
statistics for both company and admin users.

Responsibilities
----------------
1. Company dashboard
2. Admin dashboard
3. Decision support

This module MUST NOT

- perform SQL directly
- implement NLP algorithms
"""

from __future__ import annotations

from database.unit_of_work import (
    UnitOfWork,
)


class DashboardService:
    """
    Dashboard application service.
    """

    # =====================================================
    # COMPANY DASHBOARD
    # =====================================================

    def get_company_dashboard(
        self,
        company_id: int,
    ) -> dict:
        """
        Return company dashboard data.
        """

        with UnitOfWork() as uow:

            analytics = uow.analytics

            return {

                "overview": (
                    analytics.overview(
                        company_id,
                    )
                ),

                "employee_mood": (
                    analytics.employee_mood(
                        company_id,
                    )
                ),

                "monthly_sentiment": (
                    analytics.monthly_sentiment(
                        company_id,
                    )
                ),

                "rating_distribution": (
                    analytics.rating_distribution(
                        company_id,
                    )
                ),

                "top_topics": (
                    analytics.top_topics(
                        company_id,
                    )
                ),

                "keywords": (
                    analytics.top_keywords(
                        company_id,
                    )
                ),

                "recent_reviews": (

                    [

                        {

                            "date": (
                                review.review_date
                                or review.created_at.date()
                            ),

                            "job_title": (
                                review.job_title
                            ),

                            "summary": (
                                review.summary
                                or ""
                            ),

                            "rating": (
                                review.overall_rating
                            ),

                            "sentiment": (
                                review.sentiment_label
                            ),

                        }

                        for review in analytics.recent_reviews(
                            company_id,
                        )

                    ]

                ),

            }

    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    def get_admin_dashboard(
        self,
    ) -> dict:
        """
        Return admin dashboard.
        """

        with UnitOfWork() as uow:

            analytics = uow.analytics

            #
            # Convert repository output
            # into frontend response shape.
            #
            processing = {

                "pending": 0,

                "processing": 0,

                "completed": 0,

                "failed": 0,

            }

            for item in analytics.processing_status():

                status = str(
                    item["status"],
                ).lower()

                if status in processing:

                    processing[
                        status
                    ] = item["count"]

            return {

                "total_companies": (
                    analytics.total_companies()
                ),

                "total_reviews": (
                    analytics.total_reviews()
                ),

                "pending_jobs": (
                    analytics.pending_jobs()
                ),

                #
                # Simple version.
                #
                "completed_analysis": (
                    analytics.total_reviews()
                ),

                "reviews_per_company": (
                    analytics.reviews_per_company()
                ),

                "monthly_imports": (
                    analytics.monthly_imports()
                ),

                "processing_status": (
                    processing
                ),

                "latest_uploads": (

                    [

                        {

                            "upload_id": (
                                upload.id
                            ),

                            "company_name": (
                                upload.company.company_name
                            ),

                            "filename": (
                                upload.original_filename
                            ),

                            "records": (
                                upload.records_count
                            ),

                            "uploaded_at": (
                                upload.uploaded_at
                            ),

                            "status": (
                                upload.status.value
                                if hasattr(
                                    upload.status,
                                    "value",
                                )
                                else upload.status
                            ),

                        }

                        for upload in analytics.latest_uploads()

                    ]

                ),

            }

        # =====================================================
        # DECISION SUPPORT
        # =====================================================

        def get_decision_support(
            self,
            company_id: int,
        ) -> dict:
            """
            Return executive decision support.

            Placeholder implementation.
            """

            dashboard = self.get_company_dashboard(
                company_id,
            )

            overview = dashboard[
                "overview"
            ]

            total = max(
                overview[
                    "total_reviews"
                ],
                1,
            )

            positive_ratio = (

                overview[
                    "positive_reviews"
                ]

                / total

            )

            health = round(
                positive_ratio * 100,
            )

            if health >= 80:

                satisfaction = "High"

            elif health >= 60:

                satisfaction = "Medium"

            else:

                satisfaction = "Low"

            return {

                "organization_health": (
                    health
                ),

                "employee_satisfaction": (
                    satisfaction
                ),

                "executive_summary": (
                    "Decision support "
                    "summary will be "
                    "expanded later."
                ),

                "strengths": [],

                "critical_issues": [],

                "recommendations": [],

            }


# =====================================================
# FACTORY
# =====================================================

_default_dashboard_service: (
    DashboardService | None
) = None


def get_dashboard_service(
) -> DashboardService:
    """
    Return shared dashboard service.
    """

    global _default_dashboard_service

    if _default_dashboard_service is None:

        _default_dashboard_service = (
            DashboardService()
        )

    return _default_dashboard_service