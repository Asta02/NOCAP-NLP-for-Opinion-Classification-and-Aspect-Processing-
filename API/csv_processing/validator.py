"""
=========================================================
CSV Validator
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Validate parsed CSV review rows.

Responsibilities
----------------
- Validate parsed rows
- Detect duplicates
- Produce validation reports

This module MUST NOT

- read CSV files
- access the database
- perform NLP analysis
"""

from __future__ import annotations

from collections import Counter

from .schemas import (
    CSVReviewRow,
    ImportOptions,
    ValidationError,
    ValidationReport,
)


class CSVValidator:
    """
    Validate parsed CSV rows.
    """

    def __init__(
        self,
        options: ImportOptions | None = None,
    ) -> None:

        self.options = (
            options
            or ImportOptions()
        )

    # =====================================================
    # PUBLIC API
    # =====================================================

    def validate(
        self,
        rows: list[CSVReviewRow],
    ) -> ValidationReport:
        """
        Validate CSV rows.
        """

        errors: list[
            ValidationError
        ] = []

        review_counter = Counter(
            row.review_text.strip().lower()
            for row in rows
            if row.review_text.strip()
        )

        valid_rows = 0

        for index, row in enumerate(
            rows,
            start=1,
        ):

            row_errors = self._validate_row(
                row=row,
                row_number=index,
                review_counter=review_counter,
            )

            if row_errors:

                errors.extend(
                    row_errors,
                )

            else:

                valid_rows += 1

        return ValidationReport(

            valid=len(errors) == 0,

            total_rows=len(rows),

            valid_rows=valid_rows,

            invalid_rows=(
                len(rows) - valid_rows
            ),

            errors=errors,

        )

    # =====================================================
    # ROW VALIDATION
    # =====================================================

    def _validate_row(
        self,
        *,
        row: CSVReviewRow,
        row_number: int,
        review_counter: Counter[str],
    ) -> list[ValidationError]:

        errors: list[
            ValidationError
        ] = []

        if not row.review_text.strip():

            errors.append(

                ValidationError(

                    row_number=row_number,

                    field="review_text",

                    message=(
                        "Review text cannot be empty."
                    ),

                )

            )

        self._validate_rating(
            row.overall_rating,
            "overall_rating",
            row_number,
            errors,
        )

        self._validate_rating(
            row.work_life_balance,
            "work_life_balance",
            row_number,
            errors,
        )

        self._validate_rating(
            row.culture_values,
            "culture_values",
            row_number,
            errors,
        )

        self._validate_rating(
            row.career_opportunities,
            "career_opportunities",
            row_number,
            errors,
        )

        self._validate_rating(
            row.compensation_benefits,
            "compensation_benefits",
            row_number,
            errors,
        )

        self._validate_rating(
            row.senior_management,
            "senior_management",
            row_number,
            errors,
        )

        if (

            self.options.detect_duplicates

            and review_counter[
                row.review_text.strip().lower()
            ] > 1

        ):

            errors.append(

                ValidationError(

                    row_number=row_number,

                    field="review_text",

                    message=(
                        "Duplicate review detected."
                    ),

                )

            )

        return errors

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _validate_rating(
        value: float | None,
        field: str,
        row_number: int,
        errors: list[ValidationError],
    ) -> None:

        if value is None:

            return

        if not (
            1.0 <= value <= 5.0
        ):

            errors.append(

                ValidationError(

                    row_number=row_number,

                    field=field,

                    message=(
                        "Rating must be between 1 and 5."
                    ),

                )

            )


# =====================================================
# FACTORY
# =====================================================

_default_validator: (
    CSVValidator | None
) = None


def get_csv_validator() -> CSVValidator:
    """
    Return the shared validator.
    """

    global _default_validator

    if _default_validator is None:

        _default_validator = (
            CSVValidator()
        )

    return _default_validator


# =====================================================
# MAIN
# =====================================================

def main() -> None:

    from csv_processing.parser import (
        get_csv_parser,
    )

    parser = get_csv_parser()

    validator = (
        get_csv_validator()
    )

    path = input(
        "CSV path: ",
    ).strip()

    rows = parser.parse(
        path,
    )

    report = validator.validate(
        rows,
    )

    print(
        report.model_dump_json(
            indent=4,
        )
    )


if __name__ == "__main__":
    main()