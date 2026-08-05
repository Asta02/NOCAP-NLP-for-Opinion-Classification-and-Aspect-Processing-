"""
=========================================================
Upload Service
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Application service responsible for
upload lifecycle management.

Responsibilities
----------------
1. Create upload records
2. Create processing jobs
3. Execute CSV import
4. Update upload status
5. Update processing progress

This module MUST NOT

- perform SQL queries directly
- perform NLP inference
- parse CSV files
"""

from __future__ import annotations

from pathlib import Path

from csv_processing.importer import (
    CSVImporter,
)

from csv_processing.schemas import (
    ImportContext,
    ImportOptions,
    ImportSummary,
)

from database.constants import (
    JobStatus,
    UploadStatus,
)

from database.unit_of_work import (
    UnitOfWork,
)


class UploadService:
    """
    Application service for upload processing.
    """

    def __init__(
        self,
    ) -> None:

        self.importer = (
            CSVImporter()
        )

    # =====================================================
    # IMPORT
    # =====================================================
    def import_csv(
        self,
        *,
        company_id: int,
        csv_path: str | Path,
        original_filename: str,
        options: ImportOptions | None = None,
    ) -> ImportSummary:
        """
        Import one CSV dataset.
        """

        options = (
            options
            or ImportOptions()
        )

        file_path = Path(
            csv_path,
        )

        #
        # Create upload + processing job.
        #
        with UnitOfWork() as uow:

            upload = uow.uploads.create(
                company_id=company_id,
                filename=file_path.name,
                original_filename=original_filename,
                file_size=file_path.stat().st_size,
                status=UploadStatus.PROCESSING,
            )

            job = (
                uow.jobs.create(
                    upload_id=upload.id,
                    status=JobStatus.RUNNING,
                    progress=0.0,
                    current_stage="Importing CSV",
                )
            )

        #
        # Execute import.
        #
        try:

            summary = self.importer.import_file(

                csv_path=file_path,

                context=ImportContext(

                    company_id=company_id,

                    upload_id=upload.id,

                    processing_job_id=job.id,

                    options=options,

                ),

            )

            with UnitOfWork() as uow:

                uow.uploads.update_status(
                    upload.id,
                    UploadStatus.COMPLETED,
                )

                uow.jobs.complete(
                    job.id,
                )

            return summary

        except Exception as error:

            with UnitOfWork() as uow:

                uow.uploads.update_status(
                    upload.id,
                    UploadStatus.FAILED,
                )

                uow.jobs.fail(
                    job.id,
                    str(error),
                )

            raise

    # =====================================================
    # RETRIEVAL
    # =====================================================

    def list_uploads(
        self,
    ):
        """
        Return all uploads.
        """

        with UnitOfWork() as uow:

            return (
                uow.uploads.list()
            )

    def get_upload(
        self,
        upload_id: int,
    ):
        """
        Return one upload.
        """

        with UnitOfWork() as uow:

            return (
                uow.uploads.get(
                    upload_id,
                )
            )

    def list_jobs(
        self,
    ):
        """
        Return all processing jobs.
        """

        with UnitOfWork() as uow:

            return (
                uow.jobs.list()
            )

    def get_job(
        self,
        job_id: int,
    ):
        """
        Return one processing job.
        """

        with UnitOfWork() as uow:

            return (
                uow.jobs.get(
                    job_id,
                )
            )