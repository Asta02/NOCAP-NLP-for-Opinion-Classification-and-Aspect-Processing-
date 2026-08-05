##################################################################################################################################
#THIS IS OLD MODEL AND THE PURPOSE IS ONLY TO TEST THE AI. THE REAFACTORED MODELS MOVED TO database/models
##################################################################################################################################

# """
# =========================================================
# Database Models
# =========================================================

# Author  : Athar Winda
# Project : NLP for Opinion Classification and Aspect Processing

# Description
# -----------
# SQLAlchemy ORM models for storing
# review analysis results.
# """

# from __future__ import annotations

# from datetime import datetime

# from sqlalchemy import (
#     DateTime,
#     Float,
#     ForeignKey,
#     Identity,
#     Integer,
#     JSON,
#     String,
#     Text,
#     func,
# )

# from sqlalchemy.orm import (
#     Mapped,
#     mapped_column,
#     relationship,
# )

# from .base import Base


# # =====================================================
# # REVIEW
# # =====================================================


# class ReviewModel(Base):
#     """
#     Review analysis record.
#     """

#     __tablename__ = "reviews"

#     id: Mapped[int] = mapped_column(
#         Integer,
#         Identity(),
#         primary_key=True,
#     )

#     review_text: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     sentiment_label: Mapped[str] = mapped_column(
#         String(20),
#         nullable=False,
#     )

#     sentiment_label_id: Mapped[int] = mapped_column(
#         Integer,
#         nullable=False,
#     )

#     sentiment_confidence: Mapped[float] = mapped_column(
#         Float,
#         nullable=False,
#     )

#     sentiment_model_version: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     topic_id: Mapped[int] = mapped_column(
#         Integer,
#         nullable=False,
#     )

#     topic_name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     topic_probability: Mapped[float | None] = mapped_column(
#         Float,
#         nullable=True,
#     )

#     topic_keywords: Mapped[list[str]] = mapped_column(
#         JSON,
#         nullable=False,
#         default=list,
#     )

#     topic_model_version: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     processing_time_ms: Mapped[float] = mapped_column(
#         Float,
#         nullable=False,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         nullable=False,
#     )

#     aspects: Mapped[list["AspectModel"]] = relationship(
#         back_populates="review",
#         cascade="all, delete-orphan",
#         passive_deletes=True,
#     )


# # =====================================================
# # REVIEW ASPECT
# # =====================================================


# class AspectModel(Base):
#     """
#     Aspect-level sentiment result.
#     """

#     __tablename__ = "review_aspects"

#     id: Mapped[int] = mapped_column(
#         Integer,
#         Identity(),
#         primary_key=True,
#     )

#     review_id: Mapped[int] = mapped_column(
#         ForeignKey(
#             "reviews.id",
#             ondelete="CASCADE",
#         ),
#         nullable=False,
#         index=True,
#     )

#     aspect: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     phrase: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     sentiment_label: Mapped[str] = mapped_column(
#         String(20),
#         nullable=False,
#     )

#     sentiment_label_id: Mapped[int] = mapped_column(
#         Integer,
#         nullable=False,
#     )

#     sentiment_confidence: Mapped[float] = mapped_column(
#         Float,
#         nullable=False,
#     )

#     sentiment_model_version: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     review: Mapped["ReviewModel"] = relationship(
#         back_populates="aspects",
#     )