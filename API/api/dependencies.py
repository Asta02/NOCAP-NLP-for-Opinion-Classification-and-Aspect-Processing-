"""
=========================================================
FastAPI Dependencies
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Dependency providers for the FastAPI
application.
"""

from __future__ import annotations

from functools import lru_cache

from services.analysis_service import (
    AnalysisService,
)

from services.analytics_service import (
    AnalyticsService,
)

from services.upload_service import (
    UploadService,
)

from services.auth_service import (
    AuthService,
)

# =====================================================
# ANALYSIS SERVICE
# =====================================================


@lru_cache(maxsize=1)
def get_analysis_service() -> AnalysisService:
    """
    Return the shared AnalysisService instance.
    """

    return AnalysisService()


@lru_cache(maxsize=1)
def get_analytics_service() -> AnalyticsService:
    """
    Return the shared AnalyticsService instance.
    """

    return AnalyticsService()


# =====================================================
# UPLOAD SERVICE
# =====================================================


@lru_cache(maxsize=1)
def get_upload_service() -> UploadService:
    """
    Return the shared UploadService instance.
    """

    return UploadService()

# =====================================================
# AUTHENTICATOR SERVICE
# =====================================================
@lru_cache(maxsize=1)
def get_auth_service() -> AuthService:

    return AuthService()