"""
=========================================================
BERTopic Preprocessing
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Lightweight preprocessing for BERTopic.

Unlike sentiment preprocessing, this module
preserves natural language because sentence
embeddings perform best on complete text.

Responsibilities
----------------
1. Detect text column
2. Remove missing documents
3. Remove empty documents
4. Trim whitespace
5. Remove duplicates
6. Remove very short documents
7. Return clean documents
"""

from __future__ import annotations

import logging

import pandas as pd

from datasets import Dataset

from .constants import (
    PREPROCESSING_CONFIG,
    TEXT_COLUMNS,
)

# =====================================================
# LOGGING
# =====================================================

LOGGER = logging.getLogger(__name__)


# =====================================================
# VALIDATION
# =====================================================

def detect_text_column(
    df: pd.DataFrame,
) -> str:
    """
    Detect the first supported text column.
    """

    for column in TEXT_COLUMNS:

        if column in df.columns:

            LOGGER.info(
                "Using text column: %s",
                column,
            )

            return column

    raise ValueError(
        "No supported text column found. "
        f"Expected one of {TEXT_COLUMNS}."
    )


# =====================================================
# CLEANING
# =====================================================

def clean_documents(
    documents: list[str],
) -> list[str]:
    """
    Clean raw review documents.

    This function intentionally performs only
    lightweight preprocessing.
    """

    cleaned: list[str] = []

    seen: set[str] = set()

    for document in documents:

        if document is None:
            continue

        text = str(document).strip()

        if not text:
            continue

        if (
            len(text.split())
            < PREPROCESSING_CONFIG["min_document_length"]
        ):
            continue

        if PREPROCESSING_CONFIG["remove_duplicates"]:

            key = text.casefold()

            if key in seen:
                continue

            seen.add(key)

        cleaned.append(text)

    LOGGER.info(
        "Prepared %d documents.",
        len(cleaned),
    )

    return cleaned


# =====================================================
# PUBLIC API
# =====================================================

def prepare_documents(
    data: (
        pd.DataFrame
        | Dataset
    ),
) -> list[str]:
    """
    Prepare documents for BERTopic.

    Parameters
    ----------
    data
        Pandas DataFrame or Hugging Face Dataset.

    Returns
    -------
    list[str]
        Clean documents.
    """

    if isinstance(
        data,
        Dataset,
    ):
        data = data.to_pandas()

    column = detect_text_column(
        data
    )

    documents = (
        data[column]
        .dropna()
        .astype(str)
        .tolist()
    )

    return clean_documents(
        documents
    )


# =====================================================
# DATASET PIPELINE
# =====================================================

def prepare_training_documents() -> list[str]:
    """
    Load and prepare training reviews.

    Returns
    -------
    list[str]
    """

    from sentiment.dataset import (
        dataset_pipeline,
    )

    dataset = dataset_pipeline()

    train = (
        dataset["train"]
    )

    return prepare_documents(
        train
    )


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Simple preprocessing test.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    documents = (
        prepare_training_documents()
    )

    print("=" * 60)
    print("BERTopic Preprocessing")
    print("=" * 60)

    print(
        f"Documents: {len(documents)}"
    )

    print("=" * 60)

    for index, document in enumerate(
        documents[:5],
        start=1,
    ):
        print(
            f"{index}. {document}"
        )


if __name__ == "__main__":
    main()