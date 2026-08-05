"""
=========================================================
Employee Review Sentiment Analysis Pipeline
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing (NO CAP)

Description
-----------
This module performs sentiment analysis on preprocessed
employee reviews using a pretrained RoBERTa sentiment
model from Hugging Face Transformers.

Pipeline
--------
1. Load Preprocessed Dataset
2. Load Sentiment Model
3. Predict Review Sentiment
4. Append Sentiment Results
5. Dataset Summary
6. Preview Dataset
7. Save Dataset
"""

from pathlib import Path
import logging
from typing import Any, TypedDict, cast
import torch

import pandas as pd
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from transformers.pipelines import pipeline


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)


# =====================================================
# PROJECT PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

INPUT_FILE = (
    PROCESSED_DATA_DIR
    / "preprocessed_reviews.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "sentiment_reviews.csv"
)


# =====================================================
# CONSTANTS
# =====================================================

MODEL_NAME = (
    "cardiffnlp/twitter-roberta-base-sentiment-latest"
)

MAX_LENGTH = 512

BATCH_SIZE = 128

LABEL_MAPPING = {
    "positive": "Positive",
    "neutral": "Neutral",
    "negative": "Negative",
}


# =====================================================
# TYPED DICTIONARY
# =====================================================

class Prediction(TypedDict):
    """
    Sentiment prediction returned by the model.
    """

    label: str
    score: float


# =====================================================
# LOAD SENTIMENT MODEL (LAZY LOADING)
# =====================================================

_classifier = None


def get_classifier() -> Any:
    """
    Load the Hugging Face sentiment analysis pipeline
    only when it is first needed.
    """

    global _classifier

    device = 0 if torch.cuda.is_available() else -1

    if _classifier is None:

        logging.info(
            "Loading sentiment model..."
        )

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME,
            use_safetensors=True,
            torch_dtype=torch.float16,
        )

        _classifier = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=device,
        )

    return _classifier


# =====================================================
# LOAD DATASET
# =====================================================

def load_dataset(
    path: Path = INPUT_FILE
) -> pd.DataFrame:
    """
    Load the preprocessed dataset.
    """

    logging.info(
        "Loading preprocessed dataset..."
    )

    df = pd.read_csv(path)

    logging.info(
        f"Dataset shape: {df.shape}"
    )

    return df

# =====================================================
# SENTIMENT ANALYSIS
# =====================================================

def analyze_sentiment(
    df: pd.DataFrame,
    batch_size: int = BATCH_SIZE
) -> pd.DataFrame:
    """
    Predict sentiment for every review using
    batch inference.
    """

    logging.info(
        "Running sentiment analysis..."
    )

    classifier = get_classifier()

    texts = (
        df["sentiment_text"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    logging.info(
        f"Analyzing {len(texts)} reviews..."
    )

    predictions = cast(
        list[Prediction],
        classifier(
            texts,
            truncation=True,
            max_length=MAX_LENGTH,
            batch_size=batch_size,
        )
    )

    labels = []

    mapped_labels = []

    sentiment_confidence = []

    for prediction in predictions:

        raw_label = prediction["label"]

        labels.append(raw_label)

        mapped_labels.append(
            LABEL_MAPPING.get(
                raw_label.lower(),
                raw_label,
            )
        )

        sentiment_confidence.append(
            prediction["score"]
        )

    df["sentiment_label"] = labels

    df["sentiment"] = mapped_labels

    df["sentiment_confidence"] = sentiment_confidence

    logging.info(
        "Generating sentiment statistics..."
    )

    logging.info(
        "Sentiment analysis completed."
    )

    sentiment_counts = df["sentiment"].value_counts()

    logging.info(
        f"Positive : {sentiment_counts.get('Positive', 0)}"
    )

    logging.info(
        f"Neutral  : {sentiment_counts.get('Neutral', 0)}"
    )

    logging.info(
        f"Negative : {sentiment_counts.get('Negative', 0)}"
    )

    return df
# =====================================================
# DATASET SUMMARY
# =====================================================

def dataset_summary(
    df: pd.DataFrame
) -> None:
    """
    Display basic sentiment statistics.
    """

    logging.info(
        "Dataset Summary"
    )

    print("\nShape:")
    print(df.shape)

    print("\nSentiment Counts:")
    print(
        df["sentiment"]
        .value_counts()
    )

    print("\nSentiment Distribution:")
    print(
        df["sentiment"]
        .value_counts(normalize=True)
        .round(4)
    )

    print("\nAverage sentiment_confidence:")
    print(
        round(
            df["sentiment_confidence"].mean(),
            4
        )
    )


# =====================================================
# PREVIEW DATASET
# =====================================================

def preview_dataset(
    df: pd.DataFrame,
    rows: int = 5
) -> None:
    """
    Display sample sentiment predictions.
    """

    logging.info(
        "Previewing sentiment predictions..."
    )

    columns = [
        "sentiment_text",
        "sentiment_label",
        "sentiment",
        "sentiment_confidence",
    ]

    print(df[columns].head(rows))


# =====================================================
# SAVE DATASET
# =====================================================

def save_dataset(
    df: pd.DataFrame,
    output_path: Path = OUTPUT_FILE
) -> None:
    """
    Save the sentiment dataset.
    """

    logging.info(
        "Saving sentiment dataset..."
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    logging.info(
        f"Dataset saved to:\n{output_path}"
    )


# =====================================================
# SENTIMENT ANALYSIS PIPELINE
# =====================================================

def sentiment_pipeline(
    input_path: Path = INPUT_FILE
) -> pd.DataFrame:
    """
    Complete sentiment analysis pipeline.

    Workflow

    Load Dataset
        ↓
    Load Sentiment Model
        ↓
    Dataset Summary
        ↓
    Preview Dataset
        ↓
    Save Dataset
    """

    logging.info("=" * 60)
    logging.info(
        "Starting sentiment analysis pipeline"
    )
    logging.info("=" * 60)

    df = load_dataset(input_path)

    df = analyze_sentiment(df)

    dataset_summary(df)

    preview_dataset(df)

    save_dataset(df)

    logging.info(
        "Sentiment analysis completed successfully."
    )

    return df


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Entry point when running this module directly.
    """

    sentiment_pipeline()


if __name__ == "__main__":
    main()