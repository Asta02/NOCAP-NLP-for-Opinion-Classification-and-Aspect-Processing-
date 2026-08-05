"""
=========================================================
Review Keyword Model
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
ORM model representing extracted keywords
from an employee review.
"""

from __future__ import annotations

from sqlalchemy import (
    Float,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base


class ReviewKeywordModel(Base):
    """
    Extracted keyword for a review.
    """

    __tablename__ = "review_keywords"

    __table_args__ = (
        Index(
            "ix_review_keyword_score",
            "keyword",
            "score",
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
    # KEYWORD
    # =====================================================

    keyword: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    review: Mapped["ReviewModel"] = relationship(
        back_populates="keywords",
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "ReviewKeywordModel("
            f"id={self.id}, "
            f"keyword='{self.keyword}', "
            f"score={self.score:.4f}"
            ")"
        )