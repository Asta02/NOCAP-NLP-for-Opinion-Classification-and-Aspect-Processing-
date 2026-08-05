"""
=========================================================
Reviews Router
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Stored review endpoints.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from api.dependencies import (
    get_analysis_service,
)

from api.schemas.responses import (
    DeleteResponse,
    ReviewListResponse,
    StoredReviewResponse,
)

from services.analysis_service import (
    AnalysisService,
)

# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/reviews",
)

# =====================================================
# GET ALL
# =====================================================


@router.get(
    "",
    response_model=ReviewListResponse,
    summary="List Reviews",
)
def list_reviews(
    service: AnalysisService = Depends(
        get_analysis_service,
    ),
) -> ReviewListResponse:
    """
    Return all stored reviews.
    """

    reviews = (
        service.list_reviews()
    )

    return ReviewListResponse(

        total=len(reviews),

        reviews=[

            StoredReviewResponse.model_validate(
                review
            )

            for review in reviews

        ],

    )


# =====================================================
# GET ONE
# =====================================================


@router.get(
    "/{review_id}",
    response_model=StoredReviewResponse,
    summary="Get Review",
)
def get_review(
    review_id: int,
    service: AnalysisService = Depends(
        get_analysis_service,
    ),
) -> StoredReviewResponse:
    """
    Return one stored review.
    """

    review = (
        service.get_review(
            review_id
        )
    )

    if review is None:

        raise HTTPException(

            status_code=(
                status.HTTP_404_NOT_FOUND
            ),

            detail=(
                "Review not found."
            ),

        )

    return StoredReviewResponse.model_validate(
        review,
    )


# =====================================================
# DELETE
# =====================================================


@router.delete(
    "/{review_id}",
    response_model=DeleteResponse,
    summary="Delete Review",
)
def delete_review(
    review_id: int,
    service: AnalysisService = Depends(
        get_analysis_service,
    ),
) -> DeleteResponse:
    """
    Delete one stored review.
    """

    deleted = (
        service.delete_review(
            review_id
        )
    )

    if not deleted:

        raise HTTPException(

            status_code=(
                status.HTTP_404_NOT_FOUND
            ),

            detail=(
                "Review not found."
            ),

        )

    return DeleteResponse(

        success=True,

        message=(
            "Review deleted successfully."
        ),

    )