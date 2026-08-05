"""
=========================================================
Processing Job Model
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
ORM model representing an asynchronous
processing job for an uploaded dataset.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
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
    DEFAULT_JOB_PROGRESS,
    DEFAULT_JOB_STATUS,
    JobStatus,
)


class ProcessingJobModel(Base):
    """
    Processing job entity.
    """

    __tablename__ = "processing_jobs"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    # =====================================================
    # UPLOAD
    # =====================================================

    upload_id: Mapped[int] = mapped_column(
        ForeignKey(
            "uploads.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # =====================================================
    # STATUS
    # =====================================================

    status: Mapped[JobStatus] = mapped_column(
        Enum(
            JobStatus,
            native_enum=False,
        ),
        nullable=False,
        default=DEFAULT_JOB_STATUS,
        index=True,
    )

    progress: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=DEFAULT_JOB_PROGRESS,
    )

    current_stage: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # =====================================================
    # ERROR
    # =====================================================

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    upload: Mapped["UploadModel"] = relationship(
        back_populates="processing_jobs",
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "ProcessingJobModel("
            f"id={self.id}, "
            f"upload_id={self.upload_id}, "
            f"status='{self.status.value}', "
            f"progress={self.progress:.1f}"
            ")"
        )