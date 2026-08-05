"""
=========================================================
Database Constants
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Shared enums and constants for database models.
"""

from __future__ import annotations

from enum import StrEnum

# =====================================================
# COMPANY STATUS
# =====================================================


class CompanyStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"


COMPANY_STATUSES: tuple[str, ...] = tuple(
    status.value
    for status in CompanyStatus
)

DEFAULT_COMPANY_STATUS: CompanyStatus = (
    CompanyStatus.ACTIVE
)

# =====================================================
# UPLOAD STATUS
# =====================================================


class UploadStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


UPLOAD_STATUSES: tuple[str, ...] = tuple(
    status.value
    for status in UploadStatus
)

DEFAULT_UPLOAD_STATUS: UploadStatus = (
    UploadStatus.PENDING
)

# =====================================================
# PROCESSING JOB STATUS
# =====================================================


class JobStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


JOB_STATUSES: tuple[str, ...] = tuple(
    status.value
    for status in JobStatus
)

DEFAULT_JOB_STATUS: JobStatus = (
    JobStatus.PENDING
)

DEFAULT_JOB_PROGRESS: float = 0.0

# =====================================================
# EMPLOYMENT STATUS
# =====================================================


class EmploymentStatus(StrEnum):
    CURRENT = "CURRENT"
    FORMER = "FORMER"


EMPLOYMENT_STATUSES: tuple[str, ...] = tuple(
    status.value
    for status in EmploymentStatus
)