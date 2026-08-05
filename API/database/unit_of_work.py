"""
=========================================================
Unit of Work
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Unit of Work implementation for coordinating
repositories using a single SQLAlchemy session.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import (
    Session,
)

from database.session import (
    SessionLocal,
)

from database.repositories.company_repository import (
    CompanyRepository,
)

from database.repositories.processing_job_repository import (
    ProcessingJobRepository,
)

from database.repositories.review_repository import (
    ReviewRepository,
)

from database.repositories.upload_repository import (
    UploadRepository,
)


class UnitOfWork:
    """
    Coordinates repositories using a single
    SQLAlchemy session and transaction.
    """

    def __init__(
        self,
    ) -> None:

        self.session: Optional[Session] = None

        self.companies: Optional[
            CompanyRepository
        ] = None

        self.uploads: Optional[
            UploadRepository
        ] = None

        self.jobs: Optional[
            ProcessingJobRepository
        ] = None

        self.reviews: Optional[
            ReviewRepository
        ] = None

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> "UnitOfWork":

        self.session = SessionLocal()

        self.companies = (
            CompanyRepository(
                self.session,
            )
        )

        self.uploads = (
            UploadRepository(
                self.session,
            )
        )

        self.jobs = (
            ProcessingJobRepository(
                self.session,
            )
        )

        self.reviews = (
            ReviewRepository(
                self.session,
            )
        )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        if self.session is None:
            return

        try:

            if exc_type is None:

                self.session.commit()

            else:

                self.session.rollback()

        finally:

            self.session.close()

            self.session = None

            self.companies = None
            self.uploads = None
            self.jobs = None
            self.reviews = None

    # =====================================================
    # TRANSACTION CONTROL
    # =====================================================

    def commit(
        self,
    ) -> None:

        if self.session is None:

            raise RuntimeError(
                "UnitOfWork has not been entered."
            )

        self.session.commit()

    def rollback(
        self,
    ) -> None:

        if self.session is None:

            raise RuntimeError(
                "UnitOfWork has not been entered."
            )

        self.session.rollback()

    def flush(
        self,
    ) -> None:

        if self.session is None:

            raise RuntimeError(
                "UnitOfWork has not been entered."
            )

        self.session.flush()

    def close(
        self,
    ) -> None:

        if self.session is None:
            return

        self.session.close()

        self.session = None

        self.companies = None
        self.uploads = None
        self.jobs = None
        self.reviews = None