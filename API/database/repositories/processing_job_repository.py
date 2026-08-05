"""
=========================================================
Processing Job Repository
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Repository for ProcessingJobModel persistence.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    select,
)

from sqlalchemy.orm import (
    Session,
)

from database.constants import (
    JobStatus,
)

from database.models.processing_job import (
    ProcessingJobModel,
)

from database.repositories.base_repository import (
    BaseRepository,
)


class ProcessingJobRepository(
    BaseRepository[ProcessingJobModel],
):
    """
    Repository for ProcessingJobModel.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:

        super().__init__(
            session=session,
            model=ProcessingJobModel,
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        *,
        upload_id: int,
        status: JobStatus = JobStatus.PENDING,
        progress: float = 0.0,
        current_stage: str | None = None,
    ) -> ProcessingJobModel:
        """
        Create and persist a processing job.
        """

        job = ProcessingJobModel(
            upload_id=upload_id,
            status=status,
            progress=progress,
            current_stage=current_stage,
        )

        return self.add(
            job,
        )

    # =====================================================
    # LIST
    # =====================================================

    def list(
        self,
    ) -> list[ProcessingJobModel]:
        """
        Return all processing jobs.
        """

        statement = (
            select(
                ProcessingJobModel,
            )
            .order_by(
                ProcessingJobModel.started_at.desc(),
            )
        )

        return list(
            self.session.scalars(
                statement,
            )
        )

    # =====================================================
    # LOOKUP
    # =====================================================

    def get_by_upload(
        self,
        upload_id: int,
    ) -> ProcessingJobModel | None:
        """
        Return the processing job
        for an upload.
        """

        statement = (
            select(
                ProcessingJobModel,
            )
            .where(
                ProcessingJobModel.upload_id == upload_id,
            )
            .limit(1)
        )

        return self.session.scalar(
            statement,
        )

    # =====================================================
    # PROGRESS
    # =====================================================

    def update_progress(
        self,
        job_id: int,
        progress: float,
    ) -> ProcessingJobModel | None:
        """
        Update job progress.
        """

        job = self.get(
            job_id,
        )

        if job is None:
            return None

        job.progress = max(
            0.0,
            min(
                100.0,
                progress,
            ),
        )

        return self.update(
            job,
        )

    def update_stage(
        self,
        job_id: int,
        stage: str,
    ) -> ProcessingJobModel | None:
        """
        Update current pipeline stage.
        """

        job = self.get(
            job_id,
        )

        if job is None:
            return None

        job.current_stage = stage

        return self.update(
            job,
        )

    # =====================================================
    # STATUS
    # =====================================================

    def update_status(
        self,
        job_id: int,
        status: JobStatus,
    ) -> ProcessingJobModel | None:
        """
        Update job status.
        """

        job = self.get(
            job_id,
        )

        if job is None:
            return None

        job.status = status

        return self.update(
            job,
        )

    # =====================================================
    # COMPLETE
    # =====================================================

    def complete(
        self,
        job_id: int,
    ) -> ProcessingJobModel | None:
        """
        Mark a job as completed.
        """

        job = self.get(
            job_id,
        )

        if job is None:
            return None

        job.status = JobStatus.COMPLETED
        job.progress = 100.0
        job.completed_at = datetime.utcnow()

        return self.update(
            job,
        )

    # =====================================================
    # FAIL
    # =====================================================

    def fail(
        self,
        job_id: int,
        error_message: str,
    ) -> ProcessingJobModel | None:
        """
        Mark a job as failed.
        """

        job = self.get(
            job_id,
        )

        if job is None:
            return None

        job.status = JobStatus.FAILED
        job.error_message = error_message
        job.completed_at = datetime.utcnow()

        return self.update(
            job,
        )

    # =====================================================
    # ACTIVE JOBS
    # =====================================================

    def list_active(
        self,
    ) -> list[ProcessingJobModel]:
        """
        Return all active processing jobs.
        """

        statement = (
            select(
                ProcessingJobModel,
            )
            .where(
                ProcessingJobModel.status.in_(
                    (
                        JobStatus.PENDING,
                        JobStatus.RUNNING,
                    )
                )
            )
            .order_by(
                ProcessingJobModel.started_at.desc(),
            )
        )

        return list(
            self.session.scalars(
                statement,
            )
        )