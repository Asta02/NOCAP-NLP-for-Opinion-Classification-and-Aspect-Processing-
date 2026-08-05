"""
=========================================================
Review Recommendation Model
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
ORM model representing AI-generated
recommendations for an employee review.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base


class ReviewRecommendationModel(Base):
    """
    AI-generated recommendation for a review.
    """

    __tablename__ = "review_recommendations"

    __table_args__ = (
        Index(
            "ix_review_recommendation_category_priority",
            "category",
            "priority",
        ),
    )

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    # =====================================================
    # FOREIGN KEY
    # =====================================================

    review_id: Mapped[int] = mapped_column(
        ForeignKey(
            "reviews.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
        index=True,
    )

    recommendation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    review: Mapped["ReviewModel"] = relationship(
        back_populates="recommendations",
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "ReviewRecommendationModel("
            f"id={self.id}, "
            f"category='{self.category}', "
            f"priority='{self.priority}'"
            ")"
        )