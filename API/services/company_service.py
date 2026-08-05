"""
=========================================================
Company Service
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Application service responsible for
company management.

Responsibilities
----------------
1. Create companies
2. Update companies
3. Delete companies
4. Retrieve companies

This module MUST NOT

- perform SQL queries directly
- perform HTTP operations
- implement authentication
"""

from __future__ import annotations

from database.models.company import (
    CompanyModel,
)

from database.unit_of_work import (
    UnitOfWork,
)

from services.security import (
    hash_password,
)


class CompanyService:
    """
    Application service for company management.
    """

    # =====================================================
    # CREATE
    # =====================================================

    def create_company(
        self,
        *,
        company_name: str,
        industry: str,
        email: str,
        username: str,
        password: str,
        logo_url: str | None = None,
        website: str | None = None,
        country: str | None = None,
        company_size: int | None = None,
    ) -> CompanyModel:
        """
        Create a new company.
        """

        with UnitOfWork() as uow:

            if uow.companies.exists_by_email(
                email,
            ):

                raise ValueError(
                    "Email already exists.",
                )

            if uow.companies.exists_by_username(
                username,
            ):

                raise ValueError(
                    "Username already exists.",
                )

            company = CompanyModel(

                company_name=company_name,

                industry=industry,

                email=email,

                username=username,

                password_hash=hash_password(
                    password,
                ),

                logo_url=logo_url,

                website=website,

                country=country,

                company_size=company_size,

            )

            return uow.companies.create(
                company,
            )

    # =====================================================
    # RETRIEVAL
    # =====================================================

    def list_companies(
        self,
    ) -> list[CompanyModel]:
        """
        Return all companies.
        """

        with UnitOfWork() as uow:

            return (
                uow.companies.list_companies()
            )

    def get_company(
        self,
        company_id: int,
    ) -> CompanyModel | None:
        """
        Return one company.
        """

        with UnitOfWork() as uow:

            return (
                uow.companies.get(
                    company_id,
                )
            )

    # =====================================================
    # UPDATE
    # =====================================================

    def update_company(
        self,
        company_id: int,
        **fields,
    ) -> CompanyModel:
        """
        Update a company.
        """

        with UnitOfWork() as uow:

            company = (
                uow.companies.get(
                    company_id,
                )
            )

            if company is None:

                raise ValueError(
                    "Company not found.",
                )

            for key, value in fields.items():

                if (
                    value is not None
                    and hasattr(
                        company,
                        key,
                    )
                ):

                    setattr(
                        company,
                        key,
                        value,
                    )

            return (
                uow.companies.update_company(
                    company,
                )
            )

    # =====================================================
    # DELETE
    # =====================================================

    def delete_company(
        self,
        company_id: int,
    ) -> bool:
        """
        Delete a company.
        """

        with UnitOfWork() as uow:

            return (
                uow.companies.delete_company(
                    company_id,
                )
            )

    # =====================================================
    # HEALTH
    # =====================================================

    def company_count(
        self,
    ) -> int:
        """
        Return total companies.
        """

        with UnitOfWork() as uow:

            return (
                uow.companies.company_count()
            )


# =====================================================
# FACTORY
# =====================================================

_default_company_service: (
    CompanyService | None
) = None


def get_company_service(
) -> CompanyService:
    """
    Return shared company service.
    """

    global _default_company_service

    if _default_company_service is None:

        _default_company_service = (
            CompanyService()
        )

    return _default_company_service


# =====================================================
# MAIN
# =====================================================

def main() -> None:

    service = (
        get_company_service()
    )

    print(

        service.company_count(),

    )


if __name__ == "__main__":
    main()