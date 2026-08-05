"""
=========================================================
CSV Processing Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Shared schemas for CSV parsing,
validation, mapping, and import.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from database.constants import (
    EmploymentStatus,
)

# =====================================================
# CSV REVIEW ROW
# =====================================================


class CSVReviewRow(BaseModel):
    """
    One review extracted directly from a CSV file.
    """

    review_date: date | None = None

    employment_status: (
        EmploymentStatus | None
    ) = None

    job_title: str | None = None

    summary: str | None = None

    review_text: str = Field(
        min_length=1,
    )

    overall_rating: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    work_life_balance: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    culture_values: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    career_opportunities: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    compensation_benefits: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    senior_management: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    @field_validator(
        "review_text",
    )
    @classmethod
    def validate_review_text(
        cls,
        value: str,
    ) -> str:

        review = value.strip()

        if not review:
            raise ValueError(
                "Review text cannot be empty."
            )

        return review


# =====================================================
# REVIEW IMPORT DATA
# =====================================================


class ReviewImportData(BaseModel):
    """
    Normalized review produced by the mapper
    and consumed by the importer.
    """

    review_date: date | None = None

    employment_status: (
        EmploymentStatus | None
    ) = None

    job_title: str | None = None

    summary: str | None = None

    review_text: str

    overall_rating: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    work_life_balance: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    culture_values: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    career_opportunities: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    compensation_benefits: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )

    senior_management: float | None = Field(
        default=None,
        ge=1.0,
        le=5.0,
    )


# =====================================================
# COLUMN MAPPING
# =====================================================


@dataclass(
    frozen=True,
    slots=True,
)
class CSVColumns:
    """
    CSV column mapping.
    """

    review_date: str = "review_date"

    employment_status: str = (
        "employment_status"
    )

    job_title: str = "job_title"

    summary: str = "summary"

    review_text: str = "review_text"

    overall_rating: str = (
        "overall_rating"
    )

    work_life_balance: str = (
        "work_life_balance"
    )

    culture_values: str = (
        "culture_values"
    )

    career_opportunities: str = (
        "career_opportunities"
    )

    compensation_benefits: str = (
        "compensation_benefits"
    )

    senior_management: str = (
        "senior_management"
    )


# =====================================================
# IMPORT OPTIONS
# =====================================================


class ImportOptions(BaseModel):
    """
    CSV import configuration.
    """

    skip_invalid_rows: bool = True

    detect_duplicates: bool = True

    batch_size: int = Field(
        default=100,
        ge=1,
    )

    encoding: str = "utf-8"

    delimiter: str = ","

    has_header: bool = True

    columns: CSVColumns = Field(
        default_factory=CSVColumns,
    )


# =====================================================
# IMPORT CONTEXT
# =====================================================


class ImportContext(BaseModel):
    """
    Context required for an import operation.
    """

    company_id: int

    upload_id: int

    processing_job_id: int

    options: ImportOptions = Field(
        default_factory=ImportOptions,
    )


# =====================================================
# VALIDATION ERROR
# =====================================================


class ValidationError(BaseModel):
    """
    Validation error for a CSV row.
    """

    row_number: int = Field(
        ge=1,
    )

    field: str

    message: str


# =====================================================
# VALIDATION REPORT
# =====================================================


class ValidationReport(BaseModel):
    """
    CSV validation summary.
    """

    valid: bool

    total_rows: int = Field(
        ge=0,
    )

    valid_rows: int = Field(
        ge=0,
    )

    invalid_rows: int = Field(
        ge=0,
    )

    errors: list[
        ValidationError
    ] = Field(
        default_factory=list,
    )


# =====================================================
# IMPORT SUMMARY
# =====================================================


class ImportSummary(BaseModel):
    """
    CSV import result.
    """

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