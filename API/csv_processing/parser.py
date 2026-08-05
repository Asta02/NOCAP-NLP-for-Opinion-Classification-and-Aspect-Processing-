"""
=========================================================
CSV Parser
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
CSV parser responsible for reading CSV files
and converting rows into CSVReviewRow objects.

Responsibilities
----------------
- Read CSV files
- Map CSV columns
- Convert rows into CSVReviewRow

This module MUST NOT

- validate business rules
- access the database
- perform NLP analysis
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import IO

from database.constants import (
    EmploymentStatus,
)

from .schemas import (
    CSVColumns,
    CSVReviewRow,
    ImportOptions,
)

# =====================================================
# CONSTANTS
# =====================================================

_INVALID_NUMERIC_VALUES = {
    "",
    "N/A",
    "NA",
    "NULL",
    "NONE",
    "--",
}

# =====================================================
# COLUMN ALIASES
# =====================================================

_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {

    "review_date": (
        "review_date",
        "date",
    ),

    "employment_status": (
        "employment_status",
        "employment",
    ),

    "job_title": (
        "job_title",
        "position",
        "role",
    ),

    "summary": (
        "summary",
        "title",
    ),

    "review_text": (
        "review_text",
        "review",
        "text",
        "comment",
    ),

    "overall_rating": (
        "overall_rating",
        "rating",
        "score",
    ),

    "work_life_balance": (
        "work_life_balance",
    ),

    "culture_values": (
        "culture_values",
    ),

    "career_opportunities": (
        "career_opportunities",
    ),

    "compensation_benefits": (
        "compensation_benefits",
    ),

    "senior_management": (
        "senior_management",
    ),

}

# =====================================================
# PARSER
# =====================================================


class CSVParser:
    """
    CSV parser.
    """

    def __init__(
        self,
        options: ImportOptions | None = None,
    ) -> None:

        self.options = (
            options
            or ImportOptions()
        )

        self.columns = (
            self.options.columns
        )

    # =====================================================
    # PUBLIC API
    # =====================================================

    def parse(
        self,
        path: str | Path,
    ) -> list[CSVReviewRow]:

        return self.parse_file(
            path,
        )

    def parse_file(
        self,
        path: str | Path,
    ) -> list[CSVReviewRow]:

        file_path = Path(
            path,
        )

        with file_path.open(
            mode="r",
            encoding=self.options.encoding,
            newline="",
        ) as file:

            return self.parse_stream(
                file,
            )

    def parse_stream(
        self,
        stream: IO[str],
    ) -> list[CSVReviewRow]:

        reader = csv.DictReader(
            stream,
            delimiter=self.options.delimiter,
        )

        self._validate_columns(
            reader.fieldnames,
        )

        rows: list[
            CSVReviewRow
        ] = []

        for record in reader:

            rows.append(

                self._parse_row(
                    record,
                )

            )

        return rows

    # =====================================================
    # INTERNAL
    # =====================================================

    def _parse_row(
        self,
        row: dict[str, str],
    ) -> CSVReviewRow:

        columns = self.columns

        return CSVReviewRow(

            review_date=self._value(
                row,
                columns.review_date,
            ),

            employment_status=self._employment_status(
                row,
                columns.employment_status,
            ),

            job_title=self._value(
                row,
                columns.job_title,
            ),

            summary=self._value(
                row,
                columns.summary,
            ),

            review_text=(

                self._value(
                    row,
                    columns.review_text,
                )

                or ""

            ),

            overall_rating=self._float(
                row,
                columns.overall_rating,
            ),

            work_life_balance=self._float(
                row,
                columns.work_life_balance,
            ),

            culture_values=self._float(
                row,
                columns.culture_values,
            ),

            career_opportunities=self._float(
                row,
                columns.career_opportunities,
            ),

            compensation_benefits=self._float(
                row,
                columns.compensation_benefits,
            ),

            senior_management=self._float(
                row,
                columns.senior_management,
            ),

        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate_columns(
        self,
        headers: list[str] | None,
    ) -> None:

        if headers is None:

            raise ValueError(
                "CSV file has no header."
            )

        review_aliases = _COLUMN_ALIASES[
            "review_text"
        ]

        if not any(
            alias in headers
            for alias in review_aliases
        ):
            raise ValueError(
                "CSV must contain one of: "
                + ", ".join(review_aliases)
            )

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _value(
        row: dict[str, str],
        column: str,
    ) -> str | None:
        """
        Return the first non-empty value from the
        configured column or one of its aliases.
        """

        aliases = _COLUMN_ALIASES.get(
            column,
            (column,),
        )

        for alias in aliases:

            value = row.get(
                alias,
            )

            if value is None:

                continue

            value = value.strip()

            if value:

                return value

        return None

    @staticmethod
    def _float(
        row: dict[str, str],
        column: str,
    ) -> float | None:

        value = row.get(
            column,
        )

        if value is None:

            return None

        value = value.strip()

        if value.upper() in _INVALID_NUMERIC_VALUES:

            return None

        value = value.replace(
            ",",
            ".",
        )

        return float(
            value,
        )

    @staticmethod
    def _employment_status(
        row: dict[str, str],
        column: str,
    ) -> EmploymentStatus | None:

        value = row.get(
            column,
        )

        if value is None:

            return None

        value = value.strip()

        if not value:

            return None

        try:

            return EmploymentStatus(
                value,
            )

        except ValueError:

            return None


# =====================================================
# FACTORY
# =====================================================

_default_parser: CSVParser | None = None


def get_csv_parser() -> CSVParser:

    global _default_parser

    if _default_parser is None:

        _default_parser = (
            CSVParser()
        )

    return _default_parser


# =====================================================
# MAIN
# =====================================================

def main() -> None:

    parser = get_csv_parser()

    path = input(
        "CSV path: ",
    ).strip()

    rows = parser.parse(
        path,
    )

    print(
        f"\nParsed {len(rows)} rows.\n"
    )

    for row in rows[:5]:

        print(
            row.model_dump(),
        )


if __name__ == "__main__":
    main()