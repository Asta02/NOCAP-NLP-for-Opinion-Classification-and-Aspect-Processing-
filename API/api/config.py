"""
=========================================================
FastAPI Configuration
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Shared configuration for the FastAPI
application.
"""

from __future__ import annotations

# =====================================================
# API
# =====================================================

API_TITLE = (
    "Employee Feedback Analysis API"
)

API_VERSION = "1.0.0"

API_DESCRIPTION = (
    "REST API for employee feedback analysis "
    "using sentiment analysis, aspect-level "
    "sentiment analysis, and BERTopic."
)

API_PREFIX = "/api/v1"

DEBUG = True

# =====================================================
# OPENAPI
# =====================================================

OPENAPI_URL = (
    f"{API_PREFIX}/openapi.json"
)

DOCS_URL = (
    f"{API_PREFIX}/docs"
)

REDOC_URL = (
    f"{API_PREFIX}/redoc"
)

# =====================================================
# CORS
# =====================================================

ALLOW_ORIGINS: list[str] = [
    "*",
]

ALLOW_CREDENTIALS = True

ALLOW_METHODS: list[str] = [
    "*",
]

ALLOW_HEADERS: list[str] = [
    "*",
]