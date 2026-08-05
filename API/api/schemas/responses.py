"""
=========================================================
API Response Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Response models for the FastAPI application.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

# =====================================================
# STORED REVIEW
# =====================================================


class StoredReviewResponse(BaseModel):
    """
    Stored review metadata.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    review_text: str

    sentiment_label: str

    topic_name: str

    processing_time_ms: float

    created_at: datetime


# =====================================================
# REVIEW LIST
# =====================================================


class ReviewListResponse(BaseModel):
    """
    Collection of stored reviews.
    """

    total: int = Field(
        ge=0,
    )

    reviews: list[
        StoredReviewResponse
    ] = Field(
        default_factory=list,
    )


# =====================================================
# DELETE RESPONSE
# =====================================================


class DeleteResponse(BaseModel):
    """
    Delete operation response.
    """

    success: bool

    message: str


# =====================================================
# HEALTH RESPONSE
# =====================================================


class HealthResponse(BaseModel):
    """
    API health response.
    """

    status: str

    model: str

    device: str

    topic_model: str

    stored_reviews: int = Field(
        ge=0,
    )

    components: dict[
        str,
        bool,
    ]