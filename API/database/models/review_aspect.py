"""
=========================================================
Review Aspect Model
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
ORM model representing aspect-level sentiment
for a review.
"""

from __future__ import annotations

from sqlalchemy import (
    Float,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base


class ReviewAspectModel(Base):
    """
    Aspect-level sentiment for a review.
    """

    __tablename__ = "review_aspects"

    __table_args__ = (
        Index(
            "ix_review_aspect_sentiment",
            "aspect",
            "sentiment_label",
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
    # ASPECT INFORMATION
    # =====================================================

    aspect: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    phrase: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # =====================================================
    # SENTIMENT
    # =====================================================

    sentiment_label: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    sentiment_label_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    sentiment_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sentiment_model_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    review: Mapped["ReviewModel"] = relationship(
        back_populates="aspects",
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:
        return (
            "ReviewAspectModel("
            f"id={self.id}, "
            f"aspect='{self.aspect}', "
            f"sentiment='{self.sentiment_label}'"
            ")"
        )