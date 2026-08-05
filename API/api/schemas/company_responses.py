"""
=========================================================
Company Response Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Response schemas for Company API.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
)

from database.models.company import (
    CompanyModel,
)


# =====================================================
# COMPANY
# =====================================================

class CompanyResponse(
    BaseModel,
):
    """
    Company response.
    """

    company_id: int

    company_name: str

    industry: str

    email: str

    username: str

    logo_url: str | None

    website: str | None

    country: str | None

    company_size: int | None

    status: str

    created_at: datetime

    @classmethod
    def from_model(
        cls,
        company: CompanyModel,
    ) -> "CompanyResponse":
        """
        Create response from ORM model.
        """

        return cls(

            company_id=company.id,

            company_name=company.company_name,

            industry=company.industry,

            email=company.email,

            username=company.username,

            logo_url=company.logo_url,

            website=company.website,

            country=company.country,

            company_size=company.company_size,

            status=(

                company.status.value

                if hasattr(
                    company.status,
                    "value",
                )

                else str(
                    company.status,
                )

            ),

            created_at=company.created_at,

        )


# =====================================================
# COMPANY LIST
# =====================================================

class CompanyListResponse(
    BaseModel,
):
    """
    List of companies.
    """

    companies: list[
        CompanyResponse
    ]

    total: int

    @classmethod
    def from_models(
        cls,
        companies: list[
            CompanyModel,
        ],
    ) -> "CompanyListResponse":
        """
        Create response from ORM models.
        """

        return cls(

            companies=[

                CompanyResponse.from_model(
                    company,
                )

                for company in companies

            ],

            total=len(
                companies,
            ),

        )


# =====================================================
# COMPANY CREATED
# =====================================================

class CompanyCreatedResponse(
    BaseModel,
):
    """
    Company creation response.
    """

    message: str

    company: CompanyResponse

    @classmethod
    def from_model(
        cls,
        company: CompanyModel,
    ) -> "CompanyCreatedResponse":
        """
        Create response.
        """

        return cls(

            message=(
                "Company created successfully."
            ),

            company=(
                CompanyResponse.from_model(
                    company,
                )
            ),

        )


# =====================================================
# COMPANY UPDATED
# =====================================================

class CompanyUpdatedResponse(
    BaseModel,
):
    """
    Company update response.
    """

    message: str

    company: CompanyResponse

    @classmethod
    def from_model(
        cls,
        company: CompanyModel,
    ) -> "CompanyUpdatedResponse":
        """
        Create response.
        """

        return cls(

            message=(
                "Company updated successfully."
            ),

            company=(
                CompanyResponse.from_model(
                    company,
                )
            ),

        )


# =====================================================
# COMPANY DELETED
# =====================================================

class CompanyDeletedResponse(
    BaseModel,
):
    """
    Company deletion response.
    """

    message: str = (
        "Company deleted successfully."
    )