"""
=========================================================
Analysis Router
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Review analysis endpoints.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from analysis.schemas import (
    ReviewAnalysis,
)

from api.dependencies import (
    get_analysis_service,
)

from api.schemas.requests import (
    AnalyzeRequest,
)

from services.analysis_service import (
    AnalysisService,
)

# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/analysis",
)

# =====================================================
# ENDPOINTS
# =====================================================


@router.post(
    "/analyze",
    response_model=ReviewAnalysis,
    status_code=status.HTTP_200_OK,
    summary="Analyze Review",
    description=(
        "Analyze an employee review using "
        "overall sentiment analysis, aspect-level "
        "sentiment analysis, and BERTopic."
    ),
)
def analyze_review(
    request: AnalyzeRequest,
    service: AnalysisService = Depends(
        get_analysis_service,
    ),
) -> ReviewAnalysis:

    return service.analyze(
        request.review,
    )