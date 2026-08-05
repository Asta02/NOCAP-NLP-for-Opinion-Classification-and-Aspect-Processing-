"""
=========================================================
Health Router
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Health check endpoints.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
)

from api.dependencies import (
    get_analysis_service,
)

from api.schemas.responses import (
    HealthResponse,
)

from services.analysis_service import (
    AnalysisService,
)

# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/health",
)

# =====================================================
# ENDPOINTS
# =====================================================


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description=(
        "Return the current status of the "
        "Employee Feedback Analysis API."
    ),
)
def health(
    service: AnalysisService = Depends(
        get_analysis_service,
    ),
) -> HealthResponse:
    """
    Return API health information.
    """

    health = (
        service.health()
    )

    return HealthResponse(
        **health,
    )