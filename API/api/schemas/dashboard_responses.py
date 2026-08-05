"""
=========================================================
Dashboard Response Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Pydantic response schemas for company and
admin dashboard endpoints.
"""

from __future__ import annotations

from datetime import (
    date,
    datetime,
)

from pydantic import (
    BaseModel,
    Field,
)

# =====================================================
# COMPANY DASHBOARD
# =====================================================


class DashboardOverviewResponse(
    BaseModel,
):
    """
    Dashboard summary.
    """

    total_reviews: int = Field(
        ge=0,
    )

    average_rating: float = Field(
        ge=0.0,
    )

    positive_reviews: int = Field(
        ge=0,
    )

    neutral_reviews: int = Field(
        ge=0,
    )

    negative_reviews: int = Field(
        ge=0,
    )


class EmployeeMoodResponse(
    BaseModel,
):
    """
    Employee mood percentages.
    """

    positive: int = Field(
        ge=0,
        le=100,
    )

    neutral: int = Field(
        ge=0,
        le=100,
    )

    negative: int = Field(
        ge=0,
        le=100,
    )


class MonthlySentimentResponse(
    BaseModel,
):
    """
    Monthly sentiment statistics.
    """

    month: date | datetime | str

    positive: int = Field(
        ge=0,
        default=0,
    )

    neutral: int = Field(
        ge=0,
        default=0,
    )

    negative: int = Field(
        ge=0,
        default=0,
    )


class RatingDistributionResponse(
    BaseModel,
):
    """
    Rating distribution.
    """

    rating: float | None

    count: int = Field(
        ge=0,
    )


class TopTopicResponse(
    BaseModel,
):
    """
    Top topic.
    """

    topic: str | None

    count: int = Field(
        ge=0,
    )


class KeywordScoreResponse(
    BaseModel,
):
    """
    Keyword score.
    """

    keyword: str

    score: float


class RecentReviewResponse(
    BaseModel,
):
    """
    Recent review.
    """

    date: date | datetime | None

    job_title: str | None

    summary: str

    rating: float | None

    sentiment: str


class DashboardResponse(
    BaseModel,
):
    """
    Company dashboard response.
    """

    overview: DashboardOverviewResponse

    employee_mood: EmployeeMoodResponse

    monthly_sentiment: list[
        MonthlySentimentResponse
    ]

    rating_distribution: list[
        RatingDistributionResponse
    ]

    top_topics: list[
        TopTopicResponse
    ]

    keywords: list[
        KeywordScoreResponse
    ]

    recent_reviews: list[
        RecentReviewResponse
    ]


# =====================================================
# ADMIN DASHBOARD
# =====================================================


class ReviewsPerCompanyResponse(
    BaseModel,
):
    """
    Review count by company.
    """

    company_name: str

    count: int = Field(
        ge=0,
    )


class MonthlyImportResponse(
    BaseModel,
):
    """
    Monthly uploads.
    """

    month: date | datetime | str

    count: int = Field(
        ge=0,
    )


class ProcessingStatusResponse(
    BaseModel,
):
    """
    Processing job statistics.
    """

    pending: int = 0

    processing: int = 0

    completed: int = 0

    failed: int = 0


class LatestUploadResponse(
    BaseModel,
):
    """
    Recent upload.
    """

    upload_id: int

    company_name: str

    filename: str

    records: int

    uploaded_at: datetime

    status: str


class AdminDashboardResponse(
    BaseModel,
):
    """
    Admin dashboard.
    """

    total_companies: int

    total_reviews: int

    pending_jobs: int

    completed_analysis: int

    reviews_per_company: list[
        ReviewsPerCompanyResponse
    ]

    monthly_imports: list[
        MonthlyImportResponse
    ]

    processing_status: (
        ProcessingStatusResponse
    )

    latest_uploads: list[
        LatestUploadResponse
    ]


# =====================================================
# DECISION SUPPORT
# =====================================================


class RecommendationResponse(
    BaseModel,
):
    """
    Recommendation item.
    """

    priority: str

    title: str

    description: str


class DecisionSupportResponse(
    BaseModel,
):
    """
    Executive decision support.
    """

    organization_health: int = Field(
        ge=0,
        le=100,
    )

    employee_satisfaction: str

    executive_summary: str

    strengths: list[str]

    critical_issues: list[str]

    recommendations: list[
        RecommendationResponse
    ]