"""
=========================================================
Security Service
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Security utilities for authentication.

Responsibilities
----------------
1. Hash passwords
2. Verify passwords
3. Create JWT access tokens
4. Decode JWT access tokens

This module MUST NOT

- access the database
- perform HTTP operations
- implement business logic
"""

from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from passlib.context import (
    CryptContext,
)

from api.settings import (
    settings,
)

# =====================================================
# PASSWORD HASHING
# =====================================================

_pwd_context = CryptContext(
    schemes=[
        "bcrypt",
    ],
    deprecated="auto",
)

# =====================================================
# PASSWORD
# =====================================================


def hash_password(
    password: str,
) -> str:
    """
    Return a bcrypt hash.
    """

    return _pwd_context.hash(
        password,
    )


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """
    Verify password against hash.
    """

    return _pwd_context.verify(
        plain_password,
        password_hash,
    )


# =====================================================
# JWT
# =====================================================


def create_access_token(
    *,
    subject: str,
    role: str,
    company_id: int | None = None,
    expires_minutes: int = settings.JWT_EXPIRE_MINUTES,
) -> str:
    """
    Create a signed JWT access token.
    """

    expire = datetime.now(
        timezone.utc,
    ) + timedelta(
        minutes=expires_minutes,
    )

    payload: dict[str, object] = {

        "sub": subject,

        "role": role,

        "exp": expire,

    }

    if company_id is not None:

        payload["company_id"] = (
            company_id
        )

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:
    """
    Decode and validate JWT.
    """

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[
            settings.JWT_ALGORITHM,
        ],
    )


# =====================================================
# FACTORY HELPERS
# =====================================================


def is_token_valid(
    token: str,
) -> bool:
    """
    Return True if token is valid.
    """

    try:

        decode_access_token(
            token,
        )

        return True

    except jwt.PyJWTError:

        return False


# =====================================================
# MAIN
# =====================================================

def main() -> None:

    password = "admin123"

    hashed = hash_password(
        password,
    )

    print(
        "Password Hash:",
        hashed,
    )

    print(
        "Verified:",
        verify_password(
            password,
            hashed,
        ),
    )

    token = create_access_token(

        subject="demo",

        role="company",

        company_id=1,

    )

    print(
        "\nJWT:\n",
        token,
    )

    print(
        "\nDecoded:\n",
        decode_access_token(
            token,
        ),
    )


if __name__ == "__main__":
    main()