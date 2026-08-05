"""
=========================================================
Dataset Preparation Pipeline
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing (NO CAP)

Description
-----------
Prepare a reproducible dataset for supervised RoBERTa
fine-tuning.

Responsibilities
----------------
1. Load sentiment dataset
2. Validate required columns
3. Remove empty reviews
4. Encode sentiment labels
5. Create stratified train/validation/test split
6. Save split CSV files
7. Return Hugging Face DatasetDict
"""

from pathlib import Path
import logging

import pandas as pd

from datasets import (
    Dataset,
    DatasetDict,
)

from sklearn.model_selection import (
    train_test_split,
)


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)


# =====================================================
# PROJECT PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentiment_reviews.csv"
)

SPLIT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "splits"
)

TRAIN_FILE = SPLIT_DIR / "train.csv"

VALIDATION_FILE = SPLIT_DIR / "validation.csv"

TEST_FILE = SPLIT_DIR / "test.csv"

SUMMARY_FILE = SPLIT_DIR / "split_summary.csv"


# =====================================================
# CONFIGURATION
# =====================================================

TEXT_COLUMN = "sentiment_text"

LABEL_COLUMN = "sentiment"

ENCODED_LABEL_COLUMN = "label"

TRAIN_SIZE = 0.80

VALIDATION_SIZE = 0.10

TEST_SIZE = 0.10

RANDOM_STATE = 42


# =====================================================
# LABEL MAPPING
# =====================================================

LABEL2ID = {
    "Negative": 0,
    "Neutral": 1,
    "Positive": 2,
}

ID2LABEL = {
    value: key
    for key, value in LABEL2ID.items()
}


# =====================================================
# COLUMNS TO SAVE
# =====================================================

SPLIT_COLUMNS = [
    TEXT_COLUMN,
    LABEL_COLUMN,
    ENCODED_LABEL_COLUMN,
]


# =====================================================
# LOAD DATASET
# =====================================================

def load_dataset() -> pd.DataFrame:
    """
    Load sentiment dataset.
    """

    logging.info(
        "Loading dataset..."
    )

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    logging.info(
        "Loaded %d records.",
        len(df),
    )

    return df


# =====================================================
# VALIDATION
# =====================================================

def validate_dataset(
    df: pd.DataFrame,
) -> None:
    """
    Validate required columns.
    """

    required_columns = [
        TEXT_COLUMN,
        LABEL_COLUMN,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


# =====================================================
# CLEAN DATASET
# =====================================================

def clean_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove empty reviews.
    """

    logging.info(
        "Cleaning dataset..."
    )

    df = df.dropna(
        subset=[TEXT_COLUMN]
    ).copy()

    df[TEXT_COLUMN] = (
        df[TEXT_COLUMN]
        .astype(str)
    )

    df = df[
        df[TEXT_COLUMN]
        .str.strip()
        != ""
    ].copy()

    logging.info(
        "Remaining records: %d",
        len(df),
    )

    return df


# =====================================================
# ENCODE LABELS
# =====================================================

def encode_labels(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Encode sentiment labels.
    """

    logging.info(
        "Encoding labels..."
    )

    unknown_labels = (
        set(df[LABEL_COLUMN])
        - set(LABEL2ID.keys())
    )

    if unknown_labels:
        raise ValueError(
            f"Unknown labels: {unknown_labels}"
        )

    df = df.copy()

    df[ENCODED_LABEL_COLUMN] = (
        df[LABEL_COLUMN]
        .map(LABEL2ID)
    )

    return df


# =====================================================
# LABEL DISTRIBUTION
# =====================================================

def log_label_distribution(
    name: str,
    df: pd.DataFrame,
) -> None:
    """
    Log class distribution.
    """

    distribution = (
        df[LABEL_COLUMN]
        .value_counts(
            normalize=True
        )
        .sort_index()
        .mul(100)
        .round(2)
    )

    logging.info(
        "%s label distribution:\n%s",
        name,
        distribution.to_string(),
    )


# =====================================================
# VALIDATE SPLITS
# =====================================================

def validate_splits(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> None:
    """
    Validate dataset splits.
    """

    if train_df.empty:
        raise ValueError(
            "Training dataset is empty."
        )

    if validation_df.empty:
        raise ValueError(
            "Validation dataset is empty."
        )

    if test_df.empty:
        raise ValueError(
            "Test dataset is empty."
        )


# =====================================================
# SPLIT DATASET
# =====================================================

def split_dataset(
    df: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Create reproducible train/validation/test split.
    """

    logging.info(
        "Creating stratified dataset split..."
    )

    train_df, temp_df = train_test_split(
        df,
        train_size=TRAIN_SIZE,
        stratify=df[
            ENCODED_LABEL_COLUMN
        ],
        random_state=RANDOM_STATE,
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        stratify=temp_df[
            ENCODED_LABEL_COLUMN
        ],
        random_state=RANDOM_STATE,
    )

    validate_splits(
        train_df,
        validation_df,
        test_df,
    )

    total = len(df)

    logging.info(
        "Train: %d (%.2f%%)",
        len(train_df),
        len(train_df) / total * 100,
    )

    logging.info(
        "Validation: %d (%.2f%%)",
        len(validation_df),
        len(validation_df) / total * 100,
    )

    logging.info(
        "Test: %d (%.2f%%)",
        len(test_df),
        len(test_df) / total * 100,
    )

    log_label_distribution(
        "Train",
        train_df,
    )

    log_label_distribution(
        "Validation",
        validation_df,
    )

    log_label_distribution(
        "Test",
        test_df,
    )

    return (
        train_df,
        validation_df,
        test_df,
    )

# =====================================================
# SAVE SPLITS
# =====================================================

def save_splits(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> None:
    """
    Save dataset splits.
    """

    logging.info(
        "Saving dataset splits..."
    )

    SPLIT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_df = train_df[
        SPLIT_COLUMNS
    ].copy()

    validation_df = validation_df[
        SPLIT_COLUMNS
    ].copy()

    test_df = test_df[
        SPLIT_COLUMNS
    ].copy()

    train_df.to_csv(
        TRAIN_FILE,
        index=False,
    )

    validation_df.to_csv(
        VALIDATION_FILE,
        index=False,
    )

    test_df.to_csv(
        TEST_FILE,
        index=False,
    )

    summary = pd.DataFrame(
        [
            {
                "split": "train",
                "rows": len(train_df),
                **train_df[LABEL_COLUMN]
                .value_counts()
                .to_dict(),
            },
            {
                "split": "validation",
                "rows": len(validation_df),
                **validation_df[LABEL_COLUMN]
                .value_counts()
                .to_dict(),
            },
            {
                "split": "test",
                "rows": len(test_df),
                **test_df[LABEL_COLUMN]
                .value_counts()
                .to_dict(),
            },
        ]
    ).fillna(0)

    summary.to_csv(
        SUMMARY_FILE,
        index=False,
    )

    logging.info(
        "Dataset splits saved."
    )


# =====================================================
# LOAD EXISTING SPLITS
# =====================================================

def load_existing_splits() -> DatasetDict:
    """
    Load existing train/validation/test splits.
    """

    logging.info(
        "Loading existing dataset splits..."
    )

    train_df = pd.read_csv(
        TRAIN_FILE
    )

    validation_df = pd.read_csv(
        VALIDATION_FILE
    )

    test_df = pd.read_csv(
        TEST_FILE
    )

    return DatasetDict(
        {
            "train": Dataset.from_pandas(
                train_df,
                preserve_index=False,
            ),
            "validation": Dataset.from_pandas(
                validation_df,
                preserve_index=False,
            ),
            "test": Dataset.from_pandas(
                test_df,
                preserve_index=False,
            ),
        }
    )


# =====================================================
# DATASET PIPELINE
# =====================================================

def dataset_pipeline(
    recreate: bool = False,
) -> DatasetDict:
    """
    Load existing dataset splits or create
    reproducible train/validation/test splits.
    """

    if (
        not recreate
        and TRAIN_FILE.exists()
        and VALIDATION_FILE.exists()
        and TEST_FILE.exists()
    ):
        return load_existing_splits()

    df = load_dataset()

    validate_dataset(df)

    df = clean_dataset(df)

    df = encode_labels(df)

    (
        train_df,
        validation_df,
        test_df,
    ) = split_dataset(df)

    save_splits(
        train_df,
        validation_df,
        test_df,
    )

    return DatasetDict(
        {
            "train": Dataset.from_pandas(
                train_df[SPLIT_COLUMNS],
                preserve_index=False,
            ),
            "validation": Dataset.from_pandas(
                validation_df[SPLIT_COLUMNS],
                preserve_index=False,
            ),
            "test": Dataset.from_pandas(
                test_df[SPLIT_COLUMNS],
                preserve_index=False,
            ),
        }
    )


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Generate reproducible dataset splits.
    """

    dataset_pipeline(
        recreate=False,
    )


if __name__ == "__main__":
    main()