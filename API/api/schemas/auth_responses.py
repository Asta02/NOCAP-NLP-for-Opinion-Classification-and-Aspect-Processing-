"""
=========================================================
Authentication Response Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing
"""

from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
)


class CompanyInfoResponse(BaseModel):
    """
    Company information.
    """

    company_id: int
    company_name: str


class CompanyLoginResponse(BaseModel):
    """
    Company login response.
    """

    token: str

    role: Literal[
        "company",
    ]

    company: CompanyInfoResponse


class AdminLoginResponse(BaseModel):
    """
    Admin login response.
    """

    token: str

    role: Literal[
        "admin",
    ]


LoginResponse = (
    CompanyLoginResponse
    | AdminLoginResponse
)