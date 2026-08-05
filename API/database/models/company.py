"""
=========================================================
Company Model
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
ORM model representing an organization that
uploads employee review datasets.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
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
    CompanyStatus,
    DEFAULT_COMPANY_STATUS,
)


class CompanyModel(Base):
    """
    Company entity.
    """

    __tablename__ = "companies"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    # =====================================================
    # COMPANY INFORMATION
    # =====================================================

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    logo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    company_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[CompanyStatus] = mapped_column(
        Enum(
            CompanyStatus,
            native_enum=False,
        ),
        nullable=False,
        default=DEFAULT_COMPANY_STATUS,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    uploads: Mapped[list["UploadModel"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reviews: Mapped[list["ReviewModel"]] = relationship(
        back_populates="company",
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
            "CompanyModel("
            f"id={self.id}, "
            f"company_name='{self.company_name}', "
            f"industry='{self.industry}', "
            f"status='{self.status.value}'"
            ")"
        )