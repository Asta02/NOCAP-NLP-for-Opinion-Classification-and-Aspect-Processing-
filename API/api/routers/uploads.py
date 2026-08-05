"""
=========================================================
Uploads Router
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
CSV upload endpoints.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from api.schemas.upload_responses import (
    ImportResponse,
    UploadListResponse,
    UploadResponse,
)

from services.upload_service import (
    UploadService,
)

# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/uploads",
)

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(
    exist_ok=True,
)

# =====================================================
# DEPENDENCY
# =====================================================


def get_upload_service() -> UploadService:
    """
    Return UploadService instance.
    """

    return UploadService()


# =====================================================
# IMPORT CSV
# =====================================================


@router.post(
    "",
    response_model=ImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload CSV",
    description=(
        "Upload a CSV file and start the "
        "employee review import pipeline."
    ),
)
def upload_csv(
    company_id: int = Form(...),
    file: UploadFile = File(...),
    service: UploadService = Depends(
        get_upload_service,
    ),
) -> ImportResponse:
    """
    Upload and import a CSV dataset.
    """

    if not file.filename.lower().endswith(
        ".csv",
    ):

        raise HTTPException(

            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),

            detail="Only CSV files are supported.",

        )

    filename = (
        f"{uuid4().hex}_{file.filename}"
    )

    destination = (
        UPLOAD_DIRECTORY / filename
    )

    with destination.open(
        "wb",
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )

    summary = service.import_csv(

        company_id=company_id,

        csv_path=destination,

        original_filename=file.filename,

    )

    return ImportResponse(

        success=True,

        message="CSV imported successfully.",

        company_id=summary.company_id,

        upload_id=summary.upload_id,

        processing_job_id=(
            summary.processing_job_id
        ),

        imported_reviews=(
            summary.imported_reviews
        ),

        skipped_reviews=(
            summary.skipped_reviews
        ),

        processing_time_ms=(
            summary.processing_time_ms
        ),

        status=summary.status,

    )


# =====================================================
# LIST UPLOADS
# =====================================================


@router.get(
    "",
    response_model=UploadListResponse,
    summary="List Uploads",
)
def list_uploads(
    service: UploadService = Depends(
        get_upload_service,
    ),
) -> UploadListResponse:
    """
    Return all uploads.
    """

    uploads = (
        service.list_uploads()
    )

    return UploadListResponse(

        total=len(uploads),

        uploads=[

            UploadResponse.model_validate(
                upload,
            )

            for upload in uploads

        ],

    )


# =====================================================
# GET UPLOAD
# =====================================================


@router.get(
    "/{upload_id}",
    response_model=UploadResponse,
    summary="Get Upload",
)
def get_upload(
    upload_id: int,
    service: UploadService = Depends(
        get_upload_service,
    ),
) -> UploadResponse:
    """
    Return one upload.
    """

    upload = (
        service.get_upload(
            upload_id,
        )
    )

    if upload is None:

        raise HTTPException(

            status_code=(
                status.HTTP_404_NOT_FOUND
            ),

            detail="Upload not found.",

        )

    return UploadResponse.model_validate(
        upload,
    )