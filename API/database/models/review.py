"""
=========================================================
Review Model
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
ORM model representing a single employee
review and its NLP analysis.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Identity,
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
from database.constants import (
    EmploymentStatus,
)


class ReviewModel(Base):
    """
    Employee review.
    """

    __tablename__ = "reviews"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    # =====================================================
    # FOREIGN KEYS
    # =====================================================

    company_id: Mapped[int] = mapped_column(
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    upload_id: Mapped[int] = mapped_column(
        ForeignKey(
            "uploads.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # =====================================================
    # REVIEW METADATA
    # =====================================================

    review_date: Mapped[datetime | None] = mapped_column(
        Date,
        nullable=True,
    )

    employment_status: Mapped[
        EmploymentStatus | None
    ] = mapped_column(
        Enum(
            EmploymentStatus,
            native_enum=False,
        ),
        nullable=True,
    )

    job_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    review_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # =====================================================
    # RATINGS
    # =====================================================

    overall_rating: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    work_life_balance: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    culture_values: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    career_opportunities: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    compensation_benefits: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    senior_management: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
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
    # TOPIC
    # =====================================================

    topic_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    topic_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    topic_probability: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    topic_model_version: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    # =====================================================
    # PROCESSING
    # =====================================================

    processing_time_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    company: Mapped["CompanyModel"] = relationship(
        back_populates="reviews",
    )

    upload: Mapped["UploadModel"] = relationship(
        back_populates="reviews",
    )

    aspects: Mapped[
        list["ReviewAspectModel"]
    ] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    keywords: Mapped[
        list["ReviewKeywordModel"]
    ] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    recommendations: Mapped[
        list["ReviewRecommendationModel"]
    ] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "ReviewModel("
            f"id={self.id}, "
            f"job_title='{self.job_title}', "
            f"sentiment='{self.sentiment_label}', "
            f"topic='{self.topic_name}'"
            ")"
        )