"""
=========================================================
Employee Review Preprocessing Pipeline
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect
          Processing (NO CAP)

Description
-----------
This module prepares employee reviews for multiple
downstream NLP tasks.

Instead of applying a single preprocessing pipeline,
the module generates several task-specific text
representations optimized for different transformer
models.

Generated Columns
-----------------
text
    Original combined employee review.

clean_text
    Basic cleaned review used as the foundation for
    downstream preprocessing.

sentiment_text
    Clean natural-language text optimized for
    transformer-based sentiment analysis (RoBERTa).

topic_text
    Lightly normalized semantic text optimized for
    transformer-based topic modeling with BERTopic.

keyword_text
    Filtered text optimized for keyword extraction
    methods such as KeyBERT.

summary_text
    Minimally cleaned review optimized for
    abstractive summarization (BART/T5).

Architecture
------------

Raw Review
      │
      ▼
text
      │
      ▼
text_cleaning()
      │
      ▼
clean_text
      │
      ├──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
sentiment_text   topic_text   keyword_text   summary_text
      │              │              │              │
      ▼              ▼              ▼              ▼
   RoBERTa       BERTopic       KeyBERT        BART
"""

from pathlib import Path
from spacy.tokens import Doc
import logging
import re

import numpy as np
import pandas as pd
import spacy


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

RAW_DATA_DIR = (
    BASE_DIR
    / "data"
    / "raw"
)

PROCESSED_DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

INPUT_FILE = (
    RAW_DATA_DIR
    / "all_employee_reviews.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "preprocessed_reviews.csv"
)


# =====================================================
# DATASET CONSTANTS
# =====================================================

COLUMN_MAPPING = {

    "dates": "date",

    "job-title": "job_title",

    "pros&cons": "review",

    "overall-ratings": "overall_rating",

    "work-balance-stars":
    "work_life_balance",

    "culture-values-stars":
    "culture_values",

    "carrer-opportunities-stars":
    "career_opportunities",

    "comp-benefit-stars":
    "compensation_benefits",

    "senior-mangemnet-stars":
    "senior_management",

}


RATING_COLUMNS = [

    "overall_rating",

    "work_life_balance",

    "culture_values",

    "career_opportunities",

    "compensation_benefits",

    "senior_management",

]


# =====================================================
# BERTopic CONSTANTS
# =====================================================

COMPANY_NAMES = {
    "amazon",
    "apple",
    "google",
    "microsoft",
    "facebook",
    "meta",
    "oracle",
    "ibm",
    "intel",
    "adobe",
    "salesforce",
    "sap",
    "vmware",
    "dell",
    "hp",
    "uber",
    "airbnb",
    "linkedin",
}


DOMAIN_STOPWORDS = {
    "good",
    "amazing",
    "awesome",
    "retail",
    "store",
    "customer",
    "good",
    "great",
    "nice",
    "employee",
    "employees",
    "job",
    "place",
    "work",
    "working",
    "company",
    "corporate",
    "review",
    "reviews",
    "very",
    "lot",
    "thing",
    "things",
    "place",
    "con",
    "pro",
    "pros",
    "really",
    "team",
    "day",
    "year",
    "time",
    "cons",
    "get",  
    "people", 
    "go", 
    "like", 
    "one", 
    "aws",
    "qae",
    "sde",
    "sde1",
    "sde2",
    "sdet",
    "l4",
    "l5",
    "l6",
    "l7",
    "think",
    "best",
    "excellent",
    "love",
    "overall",
    "current",
    "former",
}


# =====================================================
# SPACY
# =====================================================

NLP_MODEL = "en_core_web_sm"

_nlp = None


def get_nlp():
    """
    Lazily load the spaCy model.

    The model is loaded only once and reused
    throughout the preprocessing pipeline.
    """

    global _nlp

    if _nlp is None:

        logging.info(
            "Loading spaCy model..."
        )

        _nlp = spacy.load(
            NLP_MODEL,
            disable=["parser"],
        )

    return _nlp


# =====================================================
# LOAD DATASET
# =====================================================

def load_dataset(
    path: Path,
) -> pd.DataFrame:
    """
    Load the raw employee review dataset.
    """

    logging.info(
        "Loading dataset..."
    )

    df = pd.read_csv(
        path,
        encoding="latin1",
    )

    logging.info(
        f"Dataset shape: {df.shape}"
    )

    return df


# =====================================================
# RENAME COLUMNS
# =====================================================

def rename_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Rename dataset columns into standardized names.
    """

    logging.info(
        "Renaming columns..."
    )

    return df.rename(
        columns=COLUMN_MAPPING,
    )


# =====================================================
# HANDLE MISSING VALUES
# =====================================================

def handle_missing_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Replace invalid values and fill missing text.
    """

    logging.info(
        "Handling missing values..."
    )

    df.replace(
        "none",
        np.nan,
        inplace=True,
    )

    df["summary"] = (
        df["summary"]
        .fillna("")
    )

    df["review"] = (
        df["review"]
        .fillna("")
    )

    return df


# =====================================================
# CONVERT RATINGS
# =====================================================

def convert_ratings(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert rating columns into numeric values.
    """

    logging.info(
        "Converting rating columns..."
    )

    for column in RATING_COLUMNS:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


# =====================================================
# COMBINE REVIEW TEXT
# =====================================================

def combine_text(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine review summary and review body.
    """

    logging.info(
        "Combining review text..."
    )

    df["text"] = (

        df["summary"]

        + " "

        + df["review"]

    )

    return df


# =====================================================
# REMOVE DUPLICATES
# =====================================================

def remove_duplicates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove duplicate employee reviews.
    """

    before = len(df)

    df = df.drop_duplicates(
        subset="text",
    )

    logging.info(
        f"Removed {before - len(df)} duplicate reviews."
    )

    return df


# =====================================================
# CONVERT DATES
# =====================================================

def convert_dates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert review dates into datetime format.
    """

    logging.info(
        "Converting dates..."
    )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    return df


# =====================================================
# BASIC TEXT CLEANING
# =====================================================

def text_cleaning(
    text: str,
) -> str:
    """
    Perform lightweight text cleaning.

    The resulting text serves as the common input
    for downstream NLP tasks.

    Processing Steps
    ----------------
    - Convert to lowercase
    - Remove URLs
    - Remove HTML tags
    - Remove numbers
    - Remove punctuation
    - Normalize whitespace

    Returns
    -------
    str
        Cleaned review text.
    """

    text = str(text)

    text = text.lower()

    text = re.sub(
        r"http\S+|www\S+",
        "",
        text,
    )

    text = re.sub(
        r"<.*?>",
        "",
        text,
    )

    text = re.sub(
        r"\d+",
        "",
        text,
    )

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


# =====================================================
# SUMMARY PREPROCESSING
# =====================================================

def prepare_summary_text(
    text: str,
) -> str:
    """
    Prepare text for abstractive summarization.

    Transformer summarization models such as BART
    and T5 perform best on natural language.
    Therefore, only minimal cleaning is applied.

    Processing Steps
    ----------------
    - Remove URLs
    - Remove HTML tags
    - Normalize whitespace

    Returns
    -------
    str
        Lightly cleaned review suitable for
        abstractive summarization.
    """

    text = str(text)

    text = re.sub(
        r"http\S+|www\S+",
        "",
        text,
    )

    text = re.sub(
        r"<.*?>",
        "",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text

# =====================================================
# GENERATE TASK-SPECIFIC TEXT REPRESENTATIONS
# =====================================================

def create_clean_text(
    df: pd.DataFrame,
) -> pd.DataFrame:

    logging.info(
        "Generating clean text..."
    )

    df["clean_text"] = (
        df["text"]
        .apply(text_cleaning)
    )

    return df

# SENTIMENT TEXT
def create_sentiment_text(
    df: pd.DataFrame,
) -> pd.DataFrame:

    logging.info(
        "Generating sentiment text..."
    )

    df["sentiment_text"] = (
        df["clean_text"]
    )

    return df

# SUMAMRY TEXT
def create_summary_text(
    df: pd.DataFrame,
) -> pd.DataFrame:

    logging.info(
        "Generating summary text..."
    )

    df["summary_text"] = (
        df["text"]
        .apply(
            prepare_summary_text
        )
    )

    return df

# TOPIC TEXT
SHORT_EXCEPTIONS = {
    "hr",
    "ui",
    "ux",
    "qa",
    "it",
    "ai",
    "ml",
}

def create_topic_text(
    df: pd.DataFrame,
    parsed_docs: list[Doc],
) -> pd.DataFrame:

    logging.info(
        "Generating topic text..."
    )

    topic_texts: list[str] = []

    for doc in parsed_docs:

        tokens: list[str] = []

        for token in doc:

            if token.is_space:
                continue

            if token.is_punct:
                continue

            if token.like_num:
                continue

            if token.is_stop:
                continue

            lemma = token.lemma_.lower().strip()

            if lemma == "-pron-":
                continue

            if (
                len(lemma) <= 2
                and lemma not in SHORT_EXCEPTIONS
            ):
                continue

            if lemma in COMPANY_NAMES:
                continue

            if lemma in DOMAIN_STOPWORDS:
                continue

            # Don't remove all ORG entities
            # AWS, Azure, Docker, GitHub may be topics

            tokens.append(lemma)

        topic_texts.append(
            " ".join(tokens)
        )

    df["topic_text"] = topic_texts

    return df

# KEYWORD TEXT
def create_keyword_text(
    df: pd.DataFrame,
    parsed_docs: list[Doc],
) -> pd.DataFrame:
    """
    Generate keyword representation optimized
    for KeyBERT.
    """

    logging.info(
        "Generating keyword text..."
    )

    keyword_texts: list[str] = []

    for doc in parsed_docs:

        tokens: list[str] = []

        for token in doc:

            if token.is_space:
                continue

            if token.is_punct:
                continue

            if token.is_stop:
                continue

            lemma = token.lemma_.lower().strip()

            if lemma == "-pron-":
                continue

            if len(lemma) <= 2:
                continue

            if lemma in COMPANY_NAMES:
                continue

            if lemma in DOMAIN_STOPWORDS:
                continue

            if token.pos_ not in {

                "NOUN",

                "PROPN",

                "ADJ",

            }:
                continue

            tokens.append(
                lemma
            )

        keyword_texts.append(
            " ".join(tokens)
        )

    df["keyword_text"] = keyword_texts

    return df

# =====================================================
# DATASET PREVIEW
# =====================================================

def preview_dataset(
    df: pd.DataFrame,
    rows: int = 5,
) -> None:
    """
    Display sample rows after preprocessing.
    """

    logging.info(
        "Previewing processed dataset..."
    )

    columns = [

        "text",

        "clean_text",

        "sentiment_text",

        "topic_text",

        "keyword_text",

        "summary_text",

    ]

    print()

    print(
        df[columns]
        .head(rows)
    )


# =====================================================
# DATASET SUMMARY
# =====================================================

def dataset_summary(
    df: pd.DataFrame,
) -> None:
    """
    Display dataset information after preprocessing.
    """

    logging.info(
        "Dataset Summary"
    )

    print("\nShape:")
    print(df.shape)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nData Types:")
    print(df.dtypes)

    print("\nGenerated Text Columns:")

    for column in [

        "clean_text",

        "sentiment_text",

        "topic_text",

        "keyword_text",

        "summary_text",

    ]:

        status = (
            "✓"
            if column in df.columns
            else "✗"
        )

        print(
            f"{status} {column}"
        )


# =====================================================
# SAVE DATASET
# =====================================================

def save_dataset(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Save the processed dataset.
    """

    logging.info(
        "Saving processed dataset..."
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    logging.info(
        f"Dataset saved to:\n{output_path}"
    )


# =====================================================
# PREPROCESSING PIPELINE
# =====================================================

def preprocess_reviews(
    input_path: Path = INPUT_FILE,
) -> pd.DataFrame:
    """
    Complete preprocessing pipeline.

    Workflow
    --------
    Load Dataset
        ↓
    Rename Columns
        ↓
    Handle Missing Values
        ↓
    Convert Ratings
        ↓
    Combine Review Text
        ↓
    Remove Duplicates
        ↓
    Convert Dates
        ↓
    Generate Task-Specific Text
        ↓
    Dataset Summary
        ↓
    Preview Dataset
        ↓
    Save Dataset
    """

    logging.info("=" * 60)
    logging.info("Starting preprocessing pipeline")
    logging.info("=" * 60)

    # -------------------------------------------------
    # Load Dataset
    # -------------------------------------------------

    df = load_dataset(input_path)

    # -------------------------------------------------
    # Standard Preprocessing
    # -------------------------------------------------

    df = rename_columns(df)

    df = handle_missing_values(df)

    df = convert_ratings(df)

    df = combine_text(df)

    df = remove_duplicates(df)

    df = convert_dates(df)

    # -------------------------------------------------
    # Generate Task-Specific Text
    # -------------------------------------------------

    df = generate_text_representations(df)

    # -------------------------------------------------
    # Display Results
    # -------------------------------------------------

    dataset_summary(df)

    preview_dataset(df)

    logging.info("=" * 60)
    logging.info("Preprocessing completed successfully.")
    logging.info("=" * 60)

    return df


# =====================================================
# GENERATE TASK-SPECIFIC TEXT REPRESENTATIONS
# =====================================================

def generate_text_representations(
    df: pd.DataFrame,
    batch_size: int = 512,
) -> pd.DataFrame:
    """
    Generate all task-specific text representations.

    Generated columns
    -----------------
    clean_text
    sentiment_text
    topic_text
    keyword_text
    summary_text
    """

    logging.info(
        "Generating task-specific text representations..."
    )

    # Clean text
    df = create_clean_text(df)

    # Sentiment text
    df = create_sentiment_text(df)

    # Summary text
    df = create_summary_text(df)

    # spaCy processing (only once)
    logging.info(
        "Parsing documents with spaCy..."
    )

    nlp = get_nlp()

    parsed_docs = list(
        nlp.pipe(
            df["text"],
            batch_size=batch_size,
        )
    )

    # Topic text
    df = create_topic_text(
        df,
        parsed_docs,
    )

    # Keyword text
    df = create_keyword_text(
        df,
        parsed_docs,
    )

    logging.info(
        "Generated task-specific text columns."
    )

    return df

# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Entry point for the preprocessing pipeline.
    """

    df = preprocess_reviews()

    save_dataset(
        df=df,
        output_path=OUTPUT_FILE,
    )


if __name__ == "__main__":
    main()