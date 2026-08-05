"""
=========================================================
Authentication Service
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Application service responsible for
authentication.

Responsibilities
----------------
1. Company login
2. Admin login
3. Generate JWT access token

This module MUST NOT

- perform HTTP operations
- execute SQL directly
"""

from __future__ import annotations

from api.settings import (
    settings,
)

from database.constants import (
    CompanyStatus,
)

from database.unit_of_work import (
    UnitOfWork,
)

from services.security import (
    create_access_token,
    verify_password,
)


class AuthService:
    """
    Authentication application service.
    """

    # =====================================================
    # LOGIN
    # =====================================================

    def login(
        self,
        *,
        username: str,
        password: str,
    ) -> dict:
        """
        Authenticate a user.

        Returns
        -------
        dict
            Authentication response.
        """

        #
        # Administrator
        #
        if (
            username == settings.ADMIN_USERNAME
            and password == settings.ADMIN_PASSWORD
        ):

            token = create_access_token(

                subject="admin",

                role="admin",

            )

            return {

                "token": token,

                "role": "admin",

            }

        #
        # Company
        #
        with UnitOfWork() as uow:

            company = (
                uow.companies.get_by_username(
                    username,
                )
            )

            if company is None:

                raise ValueError(
                    "Invalid username or password.",
                )

            if (
                company.status
                != CompanyStatus.ACTIVE
            ):

                raise ValueError(
                    "Company account is inactive.",
                )

            if not company.password_hash:

                raise ValueError(
                    "Password has not been configured.",
                )

            if not verify_password(

                password,

                company.password_hash,

            ):

                raise ValueError(
                    "Invalid username or password.",
                )

            token = create_access_token(

                subject=company.username,

                role="company",

                company_id=company.id,

            )

            return {

                "token": token,

                "role": "company",

                "company": {

                    "company_id": company.id,

                    "company_name": company.company_name,

                },

            }

    # =====================================================
    # VERIFY TOKEN
    # =====================================================

    def create_token(
        self,
        *,
        company_id: int,
        username: str,
    ) -> str:
        """
        Create a company JWT.
        """

        return create_access_token(

            subject=username,

            role="company",

            company_id=company_id,

        )


# =====================================================
# FACTORY
# =====================================================

_default_auth_service: (
    AuthService | None
) = None


def get_auth_service(
) -> AuthService:
    """
    Return shared AuthService.
    """

    global _default_auth_service

    if _default_auth_service is None:

        _default_auth_service = (
            AuthService()
        )

    return _default_auth_service


# =====================================================
# MAIN
# =====================================================

def main() -> None:

    service = get_auth_service()

    try:

        result = service.login(

            username="admin",

            password="admin123",

        )

        print(result)

    except Exception as exc:

        print(exc)


if __name__ == "__main__":
    main()