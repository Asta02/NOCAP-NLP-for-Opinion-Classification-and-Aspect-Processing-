"""
=========================================================
Upload Repository
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Repository for UploadModel persistence.
"""

from __future__ import annotations

from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
)

from database.constants import (
    UploadStatus,
)

from database.models.upload import (
    UploadModel,
)

from database.repositories.base_repository import (
    BaseRepository,
)


class UploadRepository(
    BaseRepository[UploadModel],
):
    """
    Repository for UploadModel.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:

        super().__init__(
            session=session,
            model=UploadModel,
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        *,
        company_id: int,
        filename: str,
        original_filename: str,
        file_size: int | None = None,
        status: UploadStatus = UploadStatus.PENDING,
    ) -> UploadModel:
        """
        Create a new upload record.
        """

        upload = UploadModel(
            company_id=company_id,
            filename=filename,
            original_filename=original_filename,
            file_size=file_size,
            status=status,
        )

        self.session.add(upload)

        self.session.flush()

        self.session.refresh(upload)

        return upload
    # =====================================================
    # LIST
    # =====================================================

    def list(
        self,
    ) -> list[UploadModel]:
        """
        Return all uploads.
        """

        statement = (
            select(
                UploadModel,
            )
            .order_by(
                UploadModel.uploaded_at.desc(),
            )
        )

        return list(
            self.session.scalars(
                statement,
            )
        )

    # =====================================================
    # COMPANY
    # =====================================================

    def list_by_company(
        self,
        company_id: int,
    ) -> list[UploadModel]:
        """
        Return uploads belonging to a company.
        """

        statement = (
            select(
                UploadModel,
            )
            .where(
                UploadModel.company_id == company_id,
            )
            .order_by(
                UploadModel.uploaded_at.desc(),
            )
        )

        return list(
            self.session.scalars(
                statement,
            )
        )

    def get_latest(
        self,
        company_id: int,
    ) -> UploadModel | None:
        """
        Return the most recent upload
        for a company.
        """

        statement = (
            select(
                UploadModel,
            )
            .where(
                UploadModel.company_id == company_id,
            )
            .order_by(
                UploadModel.uploaded_at.desc(),
            )
            .limit(1)
        )

        return self.session.scalar(
            statement,
        )

    # =====================================================
    # CHECKSUM
    # =====================================================

    def find_by_checksum(
        self,
        checksum: str,
    ) -> UploadModel | None:
        """
        Return an upload matching the checksum.
        """

        statement = (
            select(
                UploadModel,
            )
            .where(
                UploadModel.checksum == checksum,
            )
            .limit(1)
        )

        return self.session.scalar(
            statement,
        )

    # =====================================================
    # STATUS
    # =====================================================

    def update_status(
        self,
        upload_id: int,
        status: UploadStatus,
    ) -> UploadModel | None:
        """
        Update upload status.
        """

        upload = self.get(
            upload_id,
        )

        if upload is None:
            return None

        upload.status = status

        return self.update(
            upload,
        )

    # =====================================================
    # RECORD COUNT
    # =====================================================

    def update_record_count(
        self,
        upload_id: int,
        count: int,
    ) -> UploadModel | None:
        """
        Update total processed record count.
        """

        upload = self.get(
            upload_id,
        )

        if upload is None:
            return None

        upload.records_count = count

        return self.update(
            upload,
        )

    def increment_records(
        self,
        upload_id: int,
        amount: int = 1,
    ) -> UploadModel | None:
        """
        Increment processed record count.
        """

        upload = self.get(
            upload_id,
        )

        if upload is None:
            return None

        upload.records_count += amount

        return self.update(
            upload,
        )

    # =====================================================
    # FILE
    # =====================================================

    def set_checksum(
        self,
        upload_id: int,
        checksum: str,
    ) -> UploadModel | None:
        """
        Store upload checksum.
        """

        upload = self.get(
            upload_id,
        )

        if upload is None:
            return None

        upload.checksum = checksum

        return self.update(
            upload,
        )