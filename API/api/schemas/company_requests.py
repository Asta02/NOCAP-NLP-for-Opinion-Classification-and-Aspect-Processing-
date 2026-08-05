"""
=========================================================
Company Request Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Request schemas for Company API.
"""

from __future__ import annotations

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


# =====================================================
# CREATE
# =====================================================

class CreateCompanyRequest(
    BaseModel,
):
    """
    Request for creating a company.
    """

    company_name: str = Field(
        min_length=1,
        max_length=255,
    )

    industry: str = Field(
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=100,
    )

    password: str = Field(
        min_length=4,
        max_length=255,
    )

    logo_url: str | None = None

    website: str | None = None

    country: str | None = None

    company_size: int | None = Field(
        default=None,
        ge=1,
    )


# =====================================================
# UPDATE
# =====================================================

class UpdateCompanyRequest(
    BaseModel,
):
    """
    Request for updating a company.
    """

    company_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    industry: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: EmailStr | None = None

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    password: str | None = Field(
        default=None,
        min_length=4,
        max_length=255,
    )

    logo_url: str | None = None

    website: str | None = None

    country: str | None = None

    company_size: int | None = Field(
        default=None,
        ge=1,
    )

    status: str | None = None