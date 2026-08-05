"""
=========================================================
API Request Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Request models for the FastAPI application.
"""

from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


# =====================================================
# ANALYZE REQUEST
# =====================================================

class AnalyzeRequest(BaseModel):
    """
    Request body for review analysis.
    """

    review: str = Field(
        ...,
        min_length=1,
        description="Employee review to analyze.",
        examples=[
            "The salary is great, but management needs improvement.",
        ],
    )

    @field_validator("review")
    @classmethod
    def validate_review(
        cls,
        value: str,
    ) -> str:

        review = value.strip()

        if not review:

            raise ValueError(
                "Review cannot be empty."
            )

        return review