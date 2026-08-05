"""
=========================================================
Company Repository
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Repository for CompanyModel persistence.
"""

from __future__ import annotations

from sqlalchemy import (
    select,
)

from sqlalchemy.orm import (
    Session,
)

from database.models.company import (
    CompanyModel,
)

from database.repositories.base_repository import (
    BaseRepository,
)


class CompanyRepository(
    BaseRepository[CompanyModel],
):
    """
    Repository for CompanyModel.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:

        super().__init__(
            session=session,
            model=CompanyModel,
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        company: CompanyModel,
    ) -> CompanyModel:
        """
        Persist a new company.
        """

        return self.add(
            company,
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update_company(
        self,
        company: CompanyModel,
    ) -> CompanyModel:
        """
        Update a company.
        """

        return self.update(
            company,
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

        return self.delete(
            company_id,
        )

    # =====================================================
    # LOOKUPS
    # =====================================================

    def get_by_email(
        self,
        email: str,
    ) -> CompanyModel | None:
        """
        Return a company by email.
        """

        statement = (

            select(
                CompanyModel,
            )

            .where(
                CompanyModel.email == email,
            )

            .limit(
                1,
            )

        )

        return self.session.scalar(
            statement,
        )

    def get_by_username(
        self,
        username: str,
    ) -> CompanyModel | None:
        """
        Return a company by username.
        """

        statement = (

            select(
                CompanyModel,
            )

            .where(
                CompanyModel.username == username,
            )

            .limit(
                1,
            )

        )

        return self.session.scalar(
            statement,
        )

    # =====================================================
    # LIST
    # =====================================================

    def list_companies(
        self,
    ) -> list[CompanyModel]:
        """
        Return all companies.
        """

        statement = (

            select(
                CompanyModel,
            )

            .order_by(
                CompanyModel.company_name,
            )

        )

        return list(

            self.session.scalars(
                statement,
            )

        )

    # =====================================================
    # EXISTS
    # =====================================================

    def exists_by_email(
        self,
        email: str,
    ) -> bool:
        """
        Check whether an email already exists.
        """

        return (

            self.get_by_email(
                email,
            )

            is not None

        )

    def exists_by_username(
        self,
        username: str,
    ) -> bool:
        """
        Check whether a username already exists.
        """

        return (

            self.get_by_username(
                username,
            )

            is not None

        )

    # =====================================================
    # COUNTS
    # =====================================================

    def company_count(
        self,
    ) -> int:
        """
        Return total companies.
        """

        return self.count()