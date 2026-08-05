"""
=========================================================
Dashboard Router
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
REST endpoints for dashboard statistics.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
)

from api.schemas.dashboard_responses import (
    AdminDashboardResponse,
    DashboardResponse,
    DecisionSupportResponse,
)

from services.dashboard_service import (
    get_dashboard_service,
)

router = APIRouter(
    prefix="/dashboard",
    tags=[
        "Dashboard",
    ],
)

service = (
    get_dashboard_service()
)


# =====================================================
# COMPANY DASHBOARD
# =====================================================

@router.get(
    "/company/{company_id}",
    response_model=DashboardResponse,
)
def get_company_dashboard(
    company_id: int,
):
    """
    Return company dashboard.
    """

    return service.get_company_dashboard(
        company_id,
    )


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
)
def get_admin_dashboard():
    """
    Return administrator dashboard.
    """

    return service.get_admin_dashboard()


# =====================================================
# DECISION SUPPORT
# =====================================================

@router.get(
    "/company/{company_id}/decision-support",
    response_model=DecisionSupportResponse,
)
def get_decision_support(
    company_id: int,
):
    """
    Return executive decision support.
    """

    return service.get_decision_support(
        company_id,
    )