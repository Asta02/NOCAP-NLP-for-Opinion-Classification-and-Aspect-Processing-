"""
=========================================================
Analytics Router
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Analytics endpoints for dashboard
visualizations and reporting.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
)

from api.dependencies import (
    get_analytics_service,
)

from services.analytics_service import (
    AnalyticsService,
)

# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)

# =====================================================
# OVERVIEW
# =====================================================

@router.get(
    "/overview",
    summary="Dashboard Overview",
    description=(
        "Return high-level dashboard metrics."
    ),
)
def dashboard_overview(
    service: AnalyticsService = Depends(
        get_analytics_service,
    ),
):
    """
    Return dashboard overview.
    """

    return (
        service.dashboard_overview()
    )


# =====================================================
# SENTIMENT
# =====================================================

@router.get(
    "/sentiment",
    summary="Sentiment Distribution",
    description=(
        "Return the distribution of overall "
        "sentiment across all reviews."
    ),
)
def sentiment_distribution(
    service: AnalyticsService = Depends(
        get_analytics_service,
    ),
):
    """
    Return sentiment distribution.
    """

    return (
        service.sentiment_distribution()
    )


# =====================================================
# TOPICS
# =====================================================

@router.get(
    "/topics",
    summary="Topic Distribution",
    description=(
        "Return the distribution of review topics."
    ),
)
def topic_distribution(
    service: AnalyticsService = Depends(
        get_analytics_service,
    ),
):
    """
    Return topic distribution.
    """

    return (
        service.topic_distribution()
    )


# =====================================================
# ASPECTS
# =====================================================

@router.get(
    "/aspects",
    summary="Aspect Distribution",
    description=(
        "Return aspect-level sentiment statistics."
    ),
)
def aspect_distribution(
    service: AnalyticsService = Depends(
        get_analytics_service,
    ),
):
    """
    Return aspect distribution.
    """

    return (
        service.aspect_distribution()
    )


# =====================================================
# COMPANIES
# =====================================================

@router.get(
    "/companies",
    summary="Reviews Per Company",
    description=(
        "Return the number of reviews grouped "
        "by company."
    ),
)
def reviews_per_company(
    service: AnalyticsService = Depends(
        get_analytics_service,
    ),
):
    """
    Return review counts per company.
    """

    return (
        service.reviews_per_company()
    )


# =====================================================
# MONTHLY
# =====================================================

@router.get(
    "/monthly",
    summary="Monthly Reviews",
    description=(
        "Return monthly review trends."
    ),
)
def monthly_reviews(
    service: AnalyticsService = Depends(
        get_analytics_service,
    ),
):
    """
    Return monthly review statistics.
    """

    return (
        service.monthly_reviews()
    )


# =====================================================
# DASHBOARD
# =====================================================

@router.get(
    "/dashboard",
    summary="Dashboard Summary",
    description=(
        "Return the complete analytics "
        "dashboard payload."
    ),
)
def dashboard_summary(
    service: AnalyticsService = Depends(
        get_analytics_service,
    ),
):
    """
    Return dashboard summary.
    """

    return (
        service.dashboard_summary()
    )