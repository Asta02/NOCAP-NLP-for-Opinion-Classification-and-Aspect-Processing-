"""
=========================================================
Company Router
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
REST API endpoints for company management.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from api.schemas.company_requests import (
    CreateCompanyRequest,
    UpdateCompanyRequest,
)

from api.schemas.company_responses import (
    CompanyCreatedResponse,
    CompanyDeletedResponse,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdatedResponse,
)

from services.company_service import (
    get_company_service,
)

router = APIRouter(
    prefix="/companies",
    tags=[
        "Company",
    ],
)

service = (
    get_company_service()
)


# =====================================================
# HELPERS
# =====================================================

def to_response(
    company,
) -> CompanyResponse:
    """
    Convert ORM model into response schema.
    """

    return CompanyResponse(

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
            else company.status
        ),

        created_at=company.created_at,

    )


# =====================================================
# CREATE
# =====================================================

@router.post(
    "",
    response_model=CompanyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    request: CreateCompanyRequest,
):
    """
    Create a new company.
    """

    try:

        company = service.create_company(

            company_name=request.company_name,

            industry=request.industry,

            email=request.email,

            username=request.username,

            #
            # Replace with hashing later.
            #
            password_hash=request.password,

            logo_url=request.logo_url,

            website=request.website,

            country=request.country,

            company_size=request.company_size,

        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return CompanyCreatedResponse(

        message="Company created successfully.",

        company=to_response(
            company,
        ),

    )


# =====================================================
# LIST
# =====================================================

@router.get(
    "",
    response_model=CompanyListResponse,
)
def list_companies():
    """
    Return all companies.
    """

    companies = (
        service.list_companies()
    )

    return CompanyListResponse(

        companies=[

            to_response(
                company,
            )

            for company in companies

        ],

        total=len(
            companies,
        ),

    )


# =====================================================
# GET
# =====================================================

@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company(
    company_id: int,
):
    """
    Return one company.
    """

    company = service.get_company(
        company_id,
    )

    if company is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    return to_response(
        company,
    )


# =====================================================
# UPDATE
# =====================================================

@router.put(
    "/{company_id}",
    response_model=CompanyUpdatedResponse,
)
def update_company(
    company_id: int,
    request: UpdateCompanyRequest,
):
    """
    Update a company.
    """

    try:

        company = service.update_company(

            company_id,

            company_name=request.company_name,

            industry=request.industry,

            email=request.email,

            username=request.username,

            password_hash=request.password,

            logo_url=request.logo_url,

            website=request.website,

            country=request.country,

            company_size=request.company_size,

            status=request.status,

        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    return CompanyUpdatedResponse(

        message="Company updated successfully.",

        company=to_response(
            company,
        ),

    )


# =====================================================
# DELETE
# =====================================================

@router.delete(
    "/{company_id}",
    response_model=CompanyDeletedResponse,
)
def delete_company(
    company_id: int,
):
    """
    Delete a company.
    """

    deleted = service.delete_company(
        company_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    return CompanyDeletedResponse(

        message="Company deleted successfully.",

    )