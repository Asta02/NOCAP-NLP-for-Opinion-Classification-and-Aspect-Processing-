"""
=========================================================
Upload Response Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Response models for upload and processing
job endpoints.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from database.constants import (
    JobStatus,
    UploadStatus,
)

# =====================================================
# UPLOAD RESPONSE
# =====================================================


class UploadResponse(BaseModel):
    """
    Stored upload information.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    company_id: int

    filename: str

    original_filename: str

    checksum: str | None = None

    status: UploadStatus

    records_count: int = Field(
        ge=0,
    )

    uploaded_at: datetime


# =====================================================
# UPLOAD LIST RESPONSE
# =====================================================


class UploadListResponse(BaseModel):
    """
    Collection of uploads.
    """

    total: int = Field(
        ge=0,
    )

    uploads: list[
        UploadResponse
    ] = Field(
        default_factory=list,
    )


# =====================================================
# PROCESSING JOB RESPONSE
# =====================================================


class ProcessingJobResponse(BaseModel):
    """
    Processing job information.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    upload_id: int

    status: JobStatus

    progress: float = Field(
        ge=0.0,
        le=100.0,
    )

    current_stage: str | None = None

    error_message: str | None = None

    started_at: datetime

    completed_at: datetime | None = None


# =====================================================
# PROCESSING JOB LIST RESPONSE
# =====================================================


class ProcessingJobListResponse(BaseModel):
    """
    Collection of processing jobs.
    """

    total: int = Field(
        ge=0,
    )

    jobs: list[
        ProcessingJobResponse
    ] = Field(
        default_factory=list,
    )


# =====================================================
# IMPORT RESPONSE
# =====================================================


class ImportResponse(BaseModel):
    """
    Response returned after importing a CSV.
    """

    success: bool

    message: str

    company_id: int

    upload_id: int

    processing_job_id: int

    imported_reviews: int = Field(
        ge=0,
    )

    skipped_reviews: int = Field(
        ge=0,
    )

    processing_time_ms: float = Field(
        ge=0.0,
    )

    status: str