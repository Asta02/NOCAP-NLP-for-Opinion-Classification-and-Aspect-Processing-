"""
=========================================================
FastAPI Exception Handlers
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Global exception handlers for the FastAPI
application.
"""

from __future__ import annotations

from fastapi import (
    FastAPI,
    Request,
    status,
)

from fastapi.responses import (
    JSONResponse,
)

# =====================================================
# EXCEPTION HANDLERS
# =====================================================


async def value_error_handler(
    request: Request,
    exc: ValueError,
) -> JSONResponse:
    """
    Handle ValueError exceptions.
    """

    return JSONResponse(

        status_code=(
            status.HTTP_400_BAD_REQUEST
        ),

        content={
            "detail": str(exc),
        },

    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected exceptions.
    """

    return JSONResponse(

        status_code=(
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),

        content={
            "detail": (
                "Internal server error."
            ),
        },

    )


# =====================================================
# REGISTRATION
# =====================================================


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Register application exception handlers.
    """

    app.add_exception_handler(
        ValueError,
        value_error_handler,
    )

    app.add_exception_handler(
        Exception,
        generic_exception_handler,
    )