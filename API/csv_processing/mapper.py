"""
=========================================================
CSV Mapper
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Convert validated CSV rows into import-ready
objects for the persistence layer.

Responsibilities
----------------
- Transform CSVReviewRow objects
- Keep CSV parsing independent from repositories

This module MUST NOT

- access the database
- perform NLP analysis
- read CSV files
"""

from __future__ import annotations

from csv_processing.schemas import (
    CSVReviewRow,
    ReviewImportData,
)

# =====================================================
# MAPPER
# =====================================================


class CSVMapper:
    """
    Convert CSV rows into ReviewImportData.
    """

    def map(
        self,
        row: CSVReviewRow,
    ) -> ReviewImportData:
        """
        Convert one CSV row.
        """

        return ReviewImportData(

            review_date=row.review_date,

            employment_status=(
                row.employment_status
            ),

            job_title=row.job_title,

            summary=row.summary,

            review_text=row.review_text,

            overall_rating=(
                row.overall_rating
            ),

            work_life_balance=(
                row.work_life_balance
            ),

            culture_values=(
                row.culture_values
            ),

            career_opportunities=(
                row.career_opportunities
            ),

            compensation_benefits=(
                row.compensation_benefits
            ),

            senior_management=(
                row.senior_management
            ),

        )

    def map_batch(
        self,
        rows: list[CSVReviewRow],
    ) -> list[ReviewImportData]:
        """
        Convert multiple CSV rows.
        """

        return [

            self.map(
                row,
            )

            for row in rows

        ]


# =====================================================
# FACTORY
# =====================================================

_default_mapper: (
    CSVMapper | None
) = None


def get_csv_mapper() -> CSVMapper:
    """
    Return shared mapper instance.
    """

    global _default_mapper

    if _default_mapper is None:

        _default_mapper = (
            CSVMapper()
        )

    return _default_mapper


# =====================================================
# MAIN
# =====================================================

def main() -> None:

    from csv_processing.parser import (
        get_csv_parser,
    )

    parser = get_csv_parser()

    mapper = get_csv_mapper()

    path = input(
        "CSV path: ",
    ).strip()

    rows = parser.parse(
        path,
    )

    mapped = mapper.map_batch(
        rows,
    )

    if mapped:

        print(
            mapped[0].model_dump(),
        )


if __name__ == "__main__":
    main()