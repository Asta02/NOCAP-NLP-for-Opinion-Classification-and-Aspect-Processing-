"""
=========================================================
FastAPI Application
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Application entry point for the Employee
Feedback Analysis API.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.startup import startup

from api.config import (
    API_DESCRIPTION,
    API_PREFIX,
    API_TITLE,
    API_VERSION,
    DOCS_URL,
    OPENAPI_URL,
    REDOC_URL,
    ALLOW_ORIGINS,
    ALLOW_CREDENTIALS,
    ALLOW_METHODS,
    ALLOW_HEADERS,
)

from api.routers.dashboard import (
    router as dashboard_router,
)

from api.routers.companies import (
    router as company_router,
)

from api.exceptions import (
    register_exception_handlers,
)

from api.routers.analysis import (
    router as analysis_router,
)

from api.routers.health import (
    router as health_router,
)

from api.routers.reviews import (
    router as reviews_router,
)

from api.routers.analytics import (
    router as analytics_router,
)

from api.routers.uploads import (
    router as uploads_router,
)

from api.routers.jobs import (
    router as jobs_router,
)

from api.routers.auth import (
    router as auth_router,
)

# =====================================================
# APPLICATION
# =====================================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    openapi_url=OPENAPI_URL,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=ALLOW_METHODS,
    allow_headers=ALLOW_HEADERS,
)

register_exception_handlers(
    app,
)

# =====================================================
# ROUTERS
# =====================================================

app.include_router(
    health_router,
    prefix=API_PREFIX,
    tags=[
        "Health",
    ],
)

app.include_router(
    analysis_router,
    prefix=API_PREFIX,
    tags=[
        "Analysis",
    ],
)

app.include_router(
    reviews_router,
    prefix=API_PREFIX,
    tags=[
        "Reviews",
    ],
)

app.include_router(
    analytics_router,
    prefix=API_PREFIX,
    tags=[
        "Analytics",
    ],
)

app.include_router(
    uploads_router,
    prefix=API_PREFIX,
    tags=[
        "Uploads",
    ],
)

app.include_router(
    jobs_router,
    prefix=API_PREFIX,
    tags=[
        "Jobs",
    ],
)

# =====================================================
# ROOT
# =====================================================

@app.get(
    "/",
    tags=[
        "Root",
    ],
)
def root() -> dict[str, str]:
    """
    Root endpoint.
    """

    return {
        "application": API_TITLE,
        "version": API_VERSION,
        "documentation": DOCS_URL,
        "openapi": OPENAPI_URL,
    }


# =====================================================
# STARTUP
# =====================================================

@app.on_event("startup")
def startup_event() -> None:
    startup()

# =====================================================
# DASHBOARD
# =====================================================
app.include_router(
    dashboard_router,
    prefix=API_PREFIX,
    tags=[
        "Dashboard",
    ],
)

# =====================================================
# COMPANY
# =====================================================
app.include_router(
    company_router,
    prefix=API_PREFIX,
    tags=[
        "Company",
    ],
)

# =====================================================
# AUTHENTICATOR
# =====================================================
app.include_router(
    auth_router,
    prefix=API_PREFIX,
    tags=[
        "Authentication",
    ],
)