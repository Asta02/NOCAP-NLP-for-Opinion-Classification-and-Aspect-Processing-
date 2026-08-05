"""
=========================================================
CSV Importer
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Coordinate CSV parsing, validation,
analysis, and persistence.

Responsibilities
----------------
- Parse CSV
- Validate rows
- Map rows
- Analyze reviews
- Persist analysis

This module MUST NOT

- implement NLP algorithms
- execute SQL directly
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from time import perf_counter

from analysis.review_analyzer import (
    ReviewAnalyzer,
)

from csv_processing.mapper import (
    get_csv_mapper,
)

from csv_processing.parser import (
    get_csv_parser,
)

from csv_processing.schemas import (
    ImportContext,
    ImportSummary,
)

from csv_processing.validator import (
    get_csv_validator,
)

from database.unit_of_work import (
    UnitOfWork,
)


class CSVImporter:
    """
    High-level CSV import orchestrator.
    """

    def __init__(
        self,
    ) -> None:

        self.parser = (
            get_csv_parser()
        )

        self.validator = (
            get_csv_validator()
        )

        self.mapper = (
            get_csv_mapper()
        )

        self.analyzer = (
            ReviewAnalyzer()
        )

    # =====================================================
    # IMPORT
    # =====================================================

    def import_file(
        self,
        csv_path: str | Path,
        context: ImportContext,
    ) -> ImportSummary:
        """
        Import one CSV file.
        """

        start = perf_counter()

        rows = self.parser.parse(
            csv_path,
        )

        report = self.validator.validate(
            rows,
        )

        mapped_rows = self.mapper.map_batch(
            rows,
        )

        imported = 0
        skipped = 0

        with UnitOfWork() as uow:

            for row in mapped_rows:

                if (
                    report.invalid_rows > 0
                    and context.options.skip_invalid_rows
                ):
                    # Invalid rows are skipped globally.
                    # Row-level filtering can be added later.
                    pass

                #
                # Combine summary + review for NLP.
                #
                analysis_text = " ".join(

                    filter(

                        None,

                        [

                            row.summary,

                            row.review_text,

                        ],

                    )

                )

                analysis = (

                    self.analyzer.analyze(

                        analysis_text,

                    )

                )

                #
                # Ensure every review has a date.
                #
                review_date = (

                    row.review_date

                    or date.today()

                )

                uow.reviews.create(

                    analysis,

                    company_id=context.company_id,

                    upload_id=context.upload_id,

                    review_text=row.review_text,

                    review_date=review_date,

                    employment_status=row.employment_status,

                    job_title=row.job_title,

                    summary=row.summary,

                    overall_rating=row.overall_rating,

                    work_life_balance=row.work_life_balance,

                    culture_values=row.culture_values,

                    career_opportunities=row.career_opportunities,

                    compensation_benefits=row.compensation_benefits,

                    senior_management=row.senior_management,

                )

                imported += 1

        elapsed = (
            perf_counter() - start
        ) * 1000

        skipped = (
            report.invalid_rows
            if context.options.skip_invalid_rows
            else 0
        )

        return ImportSummary(

            company_id=context.company_id,

            upload_id=context.upload_id,

            processing_job_id=(
                context.processing_job_id
            ),

            imported_reviews=imported,

            skipped_reviews=skipped,

            processing_time_ms=elapsed,

            status="COMPLETED",

        )


# =====================================================
# FACTORY
# =====================================================

_default_importer: (
    CSVImporter | None
) = None


def get_csv_importer() -> CSVImporter:
    """
    Return shared importer.
    """

    global _default_importer

    if _default_importer is None:

        _default_importer = (
            CSVImporter()
        )

    return _default_importer


# =====================================================
# MAIN
# =====================================================

def main() -> None:

    from csv_processing.schemas import (
        ImportContext,
        ImportOptions,
    )

    importer = (
        get_csv_importer()
    )

    path = input(
        "CSV path: ",
    ).strip()

    summary = importer.import_file(

        path,

        ImportContext(

            company_id=1,

            upload_id=1,

            processing_job_id=1,

            options=ImportOptions(),

        ),

    )

    print(
        summary.model_dump_json(
            indent=4,
        )
    )


if __name__ == "__main__":
    main()