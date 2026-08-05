"""
=========================================================
Authentication Request Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing
"""

from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
)


class LoginRequest(BaseModel):
    """
    Login request.
    """

    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )