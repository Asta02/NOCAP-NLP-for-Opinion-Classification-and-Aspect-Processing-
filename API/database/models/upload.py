"""
=========================================================
Upload Model
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
ORM model representing an uploaded employee
review dataset.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base
from database.constants import (
    DEFAULT_UPLOAD_STATUS,
    UploadStatus,
)


class UploadModel(Base):
    """
    Uploaded dataset.
    """

    __tablename__ = "uploads"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    # =====================================================
    # COMPANY
    # =====================================================

    company_id: Mapped[int] = mapped_column(
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # =====================================================
    # FILE INFORMATION
    # =====================================================

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    records_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # =====================================================
    # STATUS
    # =====================================================

    status: Mapped[UploadStatus] = mapped_column(
        Enum(
            UploadStatus,
            native_enum=False,
        ),
        nullable=False,
        default=DEFAULT_UPLOAD_STATUS,
        index=True,
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    company: Mapped["CompanyModel"] = relationship(
        back_populates="uploads",
    )

    processing_jobs: Mapped[list["ProcessingJobModel"]] = relationship(
        back_populates="upload",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reviews: Mapped[list["ReviewModel"]] = relationship(
        back_populates="upload",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # =====================================================
    # CHECKSUM
    # =====================================================
    checksum: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "UploadModel("
            f"id={self.id}, "
            f"filename='{self.filename}', "
            f"status='{self.status.value}', "
            f"records_count={self.records_count}"
            ")"
        )