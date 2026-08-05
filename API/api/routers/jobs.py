"""
=========================================================
Processing Jobs Router
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Processing job endpoints.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from api.dependencies import (
    get_upload_service,
)

from api.schemas.upload_responses import (
    ProcessingJobListResponse,
    ProcessingJobResponse,
)

from services.upload_service import (
    UploadService,
)

# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/jobs",
)

# =====================================================
# LIST JOBS
# =====================================================


@router.get(
    "",
    response_model=ProcessingJobListResponse,
    summary="List Processing Jobs",
    description=(
        "Return all CSV processing jobs."
    ),
)
def list_jobs(
    service: UploadService = Depends(
        get_upload_service,
    ),
) -> ProcessingJobListResponse:
    """
    Return all processing jobs.
    """

    jobs = service.list_jobs()

    return ProcessingJobListResponse(

        total=len(jobs),

        jobs=[

            ProcessingJobResponse.model_validate(
                job,
            )

            for job in jobs

        ],

    )


# =====================================================
# GET JOB
# =====================================================


@router.get(
    "/{job_id}",
    response_model=ProcessingJobResponse,
    summary="Get Processing Job",
    description=(
        "Return one processing job."
    ),
)
def get_job(
    job_id: int,
    service: UploadService = Depends(
        get_upload_service,
    ),
) -> ProcessingJobResponse:
    """
    Return one processing job.
    """

    job = service.get_job(
        job_id,
    )

    if job is None:

        raise HTTPException(

            status_code=(
                status.HTTP_404_NOT_FOUND
            ),

            detail=(
                "Processing job not found."
            ),

        )

    return ProcessingJobResponse.model_validate(
        job,
    )


# =====================================================
# JOB PROGRESS
# =====================================================


@router.get(
    "/{job_id}/progress",
    summary="Processing Progress",
    description=(
        "Return processing progress for one job."
    ),
)
def job_progress(
    job_id: int,
    service: UploadService = Depends(
        get_upload_service,
    ),
) -> dict[str, object]:
    """
    Return processing progress.
    """

    job = service.get_job(
        job_id,
    )

    if job is None:

        raise HTTPException(

            status_code=(
                status.HTTP_404_NOT_FOUND
            ),

            detail=(
                "Processing job not found."
            ),

        )

    return {

        "job_id": job.id,

        "status": job.status,

        "progress": job.progress,

        "current_stage": job.current_stage,

        "error_message": job.error_message,

        "started_at": job.started_at,

        "completed_at": job.completed_at,

    }