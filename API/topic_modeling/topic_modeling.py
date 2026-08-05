"""
=========================================================
Employee Review Topic Modeling Pipeline
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing (NO CAP)

Description
-----------
This module performs topic modeling on employee reviews
using BERTopic.

BERTopic combines transformer-based sentence embeddings,
dimensionality reduction (UMAP), and density-based
clustering (HDBSCAN) to automatically discover latent
discussion topics from employee reviews.

Pipeline
--------
1. Load Sentiment Dataset
2. Load Embedding Model
3. Load BERTopic Model
4. Train BERTopic
5. Assign Topics
6. Generate Topic Summary
7. Save Topic Information
8. Save BERTopic Model
9. Generate Topic Distribution Figure
10. Save Dataset
"""

from pathlib import Path
import logging

import re
import torch
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Any, cast
from transformers.pipelines import pipeline

from sentence_transformers import SentenceTransformer

from bertopic import BERTopic
from bertopic.representation import BaseRepresentation, KeyBERTInspired, MaximalMarginalRelevance
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS

from umap import UMAP

from hdbscan import HDBSCAN


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

PROCESSED_DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

MODELS_DIR = (
    BASE_DIR
    / "models"
)

FIGURES_DIR = (
    BASE_DIR
    / "analysis"
    / "figures"
)

INPUT_FILE = (
    PROCESSED_DATA_DIR
    / "sentiment_reviews.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "topic_reviews.csv"
)

TOPIC_INFO_FILE = (
    PROCESSED_DATA_DIR
    / "topics.csv"
)

MODEL_OUTPUT_DIR = (
    MODELS_DIR
    / "bertopic_model"
)

TOPIC_DISTRIBUTION_FIGURE = (
    FIGURES_DIR
    / "topic_distribution.png"
)

TOPIC_VISUALIZATION_FILE = (
    FIGURES_DIR
    / "topic_visualization.html"
)


# =====================================================
# CONSTANTS
# =====================================================

CUSTOM_STOPWORDS = ENGLISH_STOP_WORDS.union({
    "amazon",
    "microsoft",
    "google",
    "company",
    "employee",
    "employees",
    "job",
    "work",
    "working",
    "people",
    "thing",
    "things",
    "really",
    "very",
    "good",
    "great",
    "nice",
    "best",
})

TOPIC_LABEL_MODEL = (
    "Qwen/Qwen2.5-1.5B-Instruct"
)

MAX_LABEL_TOKENS = 16

NUM_REPRESENTATIVE_DOCS = 3

EMBEDDING_MODEL_NAME = (
    "BAAI/bge-base-en-v1.5"
)

MIN_CLUSTER_SIZE = 30
MIN_TOPIC_SIZE = 40
MIN_SAMPLES = 5
TOP_N_WORDS = 20
RANDOM_STATE = 42
N_NEIGHBORS = 15
N_COMPONENTS = 5
MIN_DIST = 0.0
METRIC = "cosine"
CALCULATE_PROBABILITIES = True
VERBOSE = True


# =====================================================
# LOAD EMBEDDING MODEL (LAZY LOADING)
# =====================================================

_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """
    Load the SentenceTransformer embedding model only
    when it is first required.

    Returns
    -------
    SentenceTransformer
        Loaded embedding model.
    """

    global _embedding_model

    if _embedding_model is None:

        logging.info(
            "Loading embedding model..."
        )

        device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        logging.info(
            f"Using device: {device}"
        )

        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME,
            device=device,
        )

    return _embedding_model


# =====================================================
# LOAD BERTopic MODEL (LAZY LOADING)
# =====================================================

_topic_model: BERTopic | None = None

def get_topic_model() -> BERTopic:
    """
    Initialize BERTopic.

    Returns
    -------
    BERTopic
        Configured BERTopic instance.
    """

    global _topic_model

    if _topic_model is None:

        logging.info(
            "Initializing BERTopic..."
        )

        logging.info(
            "UMAP: n_neighbors=%d",
            N_NEIGHBORS,
        )

        logging.info(
            "HDBSCAN: min_cluster_size=%d, min_samples=%d",
            MIN_CLUSTER_SIZE,
            MIN_SAMPLES,
        )

        # -------------------------------------------------
        # UMAP
        # -------------------------------------------------

        umap_model = UMAP(
            n_neighbors=N_NEIGHBORS,
            n_components=N_COMPONENTS,
            min_dist=MIN_DIST,
            metric=METRIC,
            random_state=RANDOM_STATE,
        )

        # -------------------------------------------------
        # HDBSCAN
        # -------------------------------------------------

        hdbscan_model = HDBSCAN(
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=MIN_SAMPLES,
            prediction_data=True,
        )

        # -------------------------------------------------
        # Topic Representation
        # -------------------------------------------------

        representation_model: dict[str, BaseRepresentation] = {
            "KeyBERT": KeyBERTInspired(top_n_words=30),
            "MMR": MaximalMarginalRelevance(diversity=0.35),
        }

        # ---------------------------------------------
        # Vectorizer
        # ---------------------------------------------

        vectorizer_model = CountVectorizer(
            stop_words=list(CUSTOM_STOPWORDS),
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        )

        # ---------------------------------------------
        # BERTopic
        # ---------------------------------------------

        _topic_model = BERTopic(
            embedding_model=get_embedding_model(),
            vectorizer_model=vectorizer_model,
            representation_model=cast(
                Any,
                representation_model,
            ),
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            min_topic_size=MIN_TOPIC_SIZE,
            nr_topics=None,
            top_n_words=TOP_N_WORDS,
            calculate_probabilities=CALCULATE_PROBABILITIES,
            verbose=VERBOSE,
        )

    return _topic_model

# =====================================================
# LOAD TOPIC LABEL MODEL (LAZY LOADING)
# =====================================================

_topic_labeler = None

def get_topic_labeler():

    global _topic_labeler

    if _topic_labeler is None:

        logging.info(
            "Loading topic labeling model..."
        )

        device = (
            0
            if torch.cuda.is_available()
            else -1
        )

        _topic_labeler = pipeline(
            task="text-generation",
            model=TOPIC_LABEL_MODEL,
            device=device,
            torch_dtype=torch.float16 if torch.cuda.is_available() else None,
            model_kwargs={
                "low_cpu_mem_usage": True,
            },
        )

    return _topic_labeler

# =====================================================
# LOAD DATASET
# =====================================================

def load_dataset(
    path: Path = INPUT_FILE,
) -> pd.DataFrame:
    """
    Load the sentiment analysis dataset.

    The dataset is expected to contain at least the
    following columns:

    - topic_text
    - sentiment
    - sentiment_confidence

    Parameters
    ----------
    path : Path, default=INPUT_FILE
        Input CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.
    """

    logging.info(
        "Loading sentiment dataset..."
    )

    df = pd.read_csv(path)

    logging.info(
        f"Dataset shape: {df.shape}"
    )

    return df

# =====================================================
# TRAIN BERTopic MODEL
# =====================================================

def train_topic_model(
    df: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    BERTopic,
    pd.DataFrame,
]:
    """
    Train BERTopic using processed employee reviews.

    Pipeline:
    1. Generate embeddings from topic_text
    2. Train BERTopic
    3. Reduce BERTopic outliers
    4. Update topic representations
    5. Store final topic assignments
    6. Store valid topic probabilities where available
    7. Store topic keywords

    Parameters
    ----------
    df : pd.DataFrame
        Dataset containing processed employee reviews.

    Returns
    -------
    tuple
        (
            Updated dataframe,
            Trained BERTopic model,
            Topic information dataframe
        )
    """

    logging.info(
        "Training BERTopic..."
    )

    topic_model = get_topic_model()

    # Work on a copy to avoid modifying the caller's
    # dataframe unexpectedly.
    df = df.copy()

    # -------------------------------------------------
    # Documents used for BERTopic
    # -------------------------------------------------

    topic_docs = (
        df["topic_text"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    # -------------------------------------------------
    # Generate embeddings
    #
    # IMPORTANT:
    # Use the same text for embeddings and BERTopic
    # clustering to avoid representation mismatch.
    # -------------------------------------------------

    logging.info(
        "Generating embeddings from topic_text..."
    )

    embeddings = get_embedding_model().encode(
        topic_docs,
        show_progress_bar=True,
        convert_to_numpy=True,
        batch_size=64,
    )

    logging.info(
        "Generated %d embeddings.",
        len(embeddings),
    )

    # -------------------------------------------------
    # Train BERTopic
    # -------------------------------------------------

    topics, probabilities = topic_model.fit_transform(
        topic_docs,
        embeddings=embeddings,
    )

    # Convert to normal Python integers.
    original_topics = [
        int(topic)
        for topic in topics
    ]

    topics = original_topics.copy()

    # -------------------------------------------------
    # Initial statistics
    # -------------------------------------------------

    topic_counts = (
        pd.Series(topics)
        .value_counts()
        .sort_index()
    )

    logging.info(
        "Initial topic assignments: %d unique topics.",
        len(topic_counts),
    )

    logging.info(
        "\n%s",
        topic_counts.to_string(),
    )

    # -------------------------------------------------
    # Reduce outliers
    # -------------------------------------------------

    original_outliers = sum(
        topic == -1
        for topic in topics
    )

    logging.info(
        "Original outliers: %d",
        original_outliers,
    )

    if original_outliers > 0:

        logging.info(
            "Reducing BERTopic outliers..."
        )

        reduced_topics = topic_model.reduce_outliers(
            documents=topic_docs,
            topics=topics,
            embeddings=embeddings,
            strategy="embeddings",
        )

        topics = [
            int(topic)
            for topic in reduced_topics
        ]

    else:

        logging.info(
            "No outliers found. "
            "Skipping outlier reduction."
        )

    # -------------------------------------------------
    # Update topic representations
    #
    # IMPORTANT:
    #
    # reduce_outliers() changes document assignments but
    # does not automatically rebuild the topic
    # representations.
    #
    # update_topics() rebuilds c-TF-IDF/topic words using
    # the final assignments.
    # -------------------------------------------------

    logging.info(
        "Updating topic representations..."
    )

    topic_model.update_topics(
        docs=topic_docs,
        topics=topics,
    )

    # Keep the model's stored assignments synchronized
    # with the assignments used by this pipeline.
    topic_model.topics_ = topics

    # -------------------------------------------------
    # Final outlier statistics
    # -------------------------------------------------

    reduced_outliers = sum(
        topic == -1
        for topic in topics
    )

    recovered_reviews = (
        original_outliers
        - reduced_outliers
    )

    logging.info(
        "Remaining outliers: %d",
        reduced_outliers,
    )

    logging.info(
        "Recovered reviews: %d",
        recovered_reviews,
    )

    # -------------------------------------------------
    # Store final topic assignment
    # -------------------------------------------------

    df["topic_id"] = topics

    # -------------------------------------------------
    # Store topic probability
    #
    # IMPORTANT:
    #
    # The probabilities returned by fit_transform()
    # describe the ORIGINAL topic assignment.
    #
    # If reduce_outliers() changes a document from -1 to
    # another topic, the original probability must NOT be
    # attached to that new topic.
    #
    # Therefore:
    #
    # unchanged assignment -> retain original probability
    # changed assignment   -> None
    #
    # This prevents misleading dashboard values.
    # -------------------------------------------------

    topic_probability: list[
        float | None
    ] = []

    if probabilities is None:

        topic_probability = [
            None
            for _ in topics
        ]

    else:

        for index, final_topic in enumerate(topics):

            original_topic = original_topics[index]

            # -----------------------------------------
            # Assignment changed during outlier
            # reduction.
            # -----------------------------------------

            if original_topic != final_topic:

                topic_probability.append(
                    None
                )

                continue

            probability = probabilities[index]

            # -----------------------------------------
            # Missing probability
            # -----------------------------------------

            if probability is None:

                topic_probability.append(
                    None
                )

                continue

            # -----------------------------------------
            # Normalize probability
            #
            # BERTopic may return either:
            # - a scalar probability
            # - a vector of topic probabilities
            #
            # Explicitly converting to float64 removes
            # the type ambiguity reported by Pylance.
            # -----------------------------------------

            probability_array = np.asarray(
                probability,
                dtype=np.float64,
            )

            # -----------------------------------------
            # Empty probability array
            # -----------------------------------------

            if probability_array.size == 0:

                topic_probability.append(
                    None
                )

                continue

            # -----------------------------------------
            # Scalar probability
            # -----------------------------------------

            if probability_array.ndim == 0:

                topic_probability.append(
                    probability_array.item()
                )

                continue

            # -----------------------------------------
            # Probability vector
            # -----------------------------------------

            topic_probability.append(
                np.max(
                    probability_array
                ).item()
            )

    df["topic_probability"] = (
        topic_probability
    )

    # -------------------------------------------------
    # Store topic keywords
    # -------------------------------------------------

    topic_keywords: list[str] = []

    for topic in topics:

        if topic == -1:

            topic_keywords.append(
                "Outlier"
            )

            continue

        words = cast(
            list[tuple[str, float]] | None,
            topic_model.get_topic(
                topic
            ),
        )

        if not words:

            topic_keywords.append(
                "Unknown"
            )

            continue

        keyword_text = ", ".join(
            word
            for word, _
            in words[:5]
        )

        topic_keywords.append(
            keyword_text
        )

    df["topic_keywords"] = (
        topic_keywords
    )

    # -------------------------------------------------
    # Topic information
    # -------------------------------------------------

    topic_info = cast(
        pd.DataFrame,
        topic_model.get_topic_info(),
    )

    # -------------------------------------------------
    # Internal BERTopic topic name
    #
    # This is useful for analysis but should NOT be the
    # primary dashboard category.
    # -------------------------------------------------

    topic_name_mapping: dict[
        int,
        str,
    ] = {}

    for topic_id in topic_info["Topic"]:

        topic_id = int(
            topic_id
        )

        if topic_id == -1:

            topic_name_mapping[
                topic_id
            ] = "Outlier"

            continue

        words = cast(
            list[tuple[str, float]] | None,
            topic_model.get_topic(
                topic_id
            ),
        )

        if not words:

            topic_name_mapping[
                topic_id
            ] = "Unknown"

            continue

        topic_name_mapping[
            topic_id
        ] = ", ".join(
            word
            for word, _
            in words[:5]
        )

    df["topic_name"] = (
        df["topic_id"]
        .map(topic_name_mapping)
        .fillna("Outlier")
    )

    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    number_of_topics = (
        topic_info[
            topic_info["Topic"] != -1
        ]
        .shape[0]
    )

    valid_probabilities = (
        df["topic_probability"]
        .notna()
        .sum()
    )

    logging.info(
        "Topic modeling completed."
    )

    logging.info(
        "Topics discovered: %d",
        number_of_topics,
    )

    if number_of_topics > 100:
        logging.warning(
            "BERTopic discovered %d latent topics. "
            "This is not automatically an error: BERTopic "
            "topics are finer-grained than the controlled "
            "business categories. Inspect coherence before "
            "forcing topic reduction.",
            number_of_topics,
        )

    logging.info(
        "Final outlier reviews: %d",
        reduced_outliers,
    )

    logging.info(
        "Reviews with valid topic probability: %d/%d",
        valid_probabilities,
        len(df),
    )

    return (
        df,
        topic_model,
        topic_info,
    )

# =====================================================
# GENERATE TOPIC SUMMARY
# =====================================================

def generate_topic_summary(
    topic_info: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create a simplified topic summary table.

    BERTopic returns many columns useful for model
    inspection. This function keeps the columns most
    useful for reporting and dashboards.

    Parameters
    ----------
    topic_info : pd.DataFrame
        Topic information returned by BERTopic.

    Returns
    -------
    pd.DataFrame
        Simplified topic summary.
    """

    logging.info(
        "Generating topic summary..."
    )

    summary = topic_info.copy()

    # -------------------------------------------------
    # Rename BERTopic columns
    # -------------------------------------------------

    rename_mapping = {
        "Topic": "topic_id",
        "Count": "document_count",
        "Name": "topic_name",
        "Representation":
            "representative_words",
    }

    summary = summary.rename(
        columns=rename_mapping
    )

    # -------------------------------------------------
    # Keep useful columns
    # -------------------------------------------------

    columns = [
        "topic_id",
        "document_count",
        "topic_name",
        "representative_words",
    ]

    summary = summary[
        [
            column
            for column in columns
            if column in summary.columns
        ]
    ].copy()

    # -------------------------------------------------
    # Normalize topic ID
    # -------------------------------------------------

    if "topic_id" in summary.columns:

        summary["topic_id"] = (
            summary["topic_id"]
            .astype(int)
        )

    # -------------------------------------------------
    # Convert representative word lists to readable
    # comma-separated strings.
    # -------------------------------------------------

    if (
        "representative_words"
        in summary.columns
    ):

        summary[
            "representative_words"
        ] = (
            summary[
                "representative_words"
            ]
            .apply(
                lambda words: (
                    ", ".join(
                        str(word)
                        for word in words
                    )
                    if isinstance(
                        words,
                        (list, tuple)
                    )
                    else words
                )
            )
        )

    logging.info(
        "Generated summary for %d topics.",
        len(summary),
    )

    return summary

# =====================================================
# GENERATE TOPIC CATEGORIES
# =====================================================

def generate_topic_labels(
    topic_model: BERTopic,
    topic_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Classify each BERTopic topic into exactly one
    controlled business category.

    The language model acts only as a classifier.

    Any output outside the allowed taxonomy is rejected
    and replaced with "Other".

    Parameters
    ----------
    topic_model : BERTopic
        Trained BERTopic model.

    topic_summary : pd.DataFrame
        Topic-level summary dataframe.

    Returns
    -------
    pd.DataFrame
        Topic summary with topic_category.
    """

    logging.info(
        "Generating topic categories..."
    )

    generator = get_topic_labeler()

    # -------------------------------------------------
    # Controlled business taxonomy
    # -------------------------------------------------

    CATEGORY_LABELS = [
        "Career Growth",
        "Compensation",
        "Leadership",
        "Work-Life Balance",
        "Benefits",
        "Workplace Culture",
        "Management",
        "Training",
        "Technology",
        "Customer Service",
        "Facilities",
        "Hiring",
        "Scheduling",
        "Remote Work",
        "Other",
    ]

    # -------------------------------------------------
    # Normalized lookup
    # -------------------------------------------------

    category_lookup = {
        category.lower(): category
        for category in CATEGORY_LABELS
    }

    topic_categories: list[str] = []

    # -------------------------------------------------
    # Classify every topic
    # -------------------------------------------------

    for topic_id in topic_summary["topic_id"]:

        topic_id = int(
            topic_id
        )

        # -------------------------------------------------
        # Outlier
        # -------------------------------------------------

        if topic_id == -1:

            topic_categories.append(
                "Other"
            )

            continue

        # -------------------------------------------------
        # Topic keywords
        # -------------------------------------------------

        keywords = cast(
            list[tuple[str, float]] | None,
            topic_model.get_topic(
                topic_id
            ),
        )

        if not keywords:

            topic_categories.append(
                "Other"
            )

            logging.warning(
                "No keywords available for topic %d. "
                "Using Other.",
                topic_id,
            )

            continue

        keyword_text = ", ".join(
            word
            for word, _
            in keywords[:8]
        )

        # -------------------------------------------------
        # Representative reviews
        # -------------------------------------------------

        representative_docs = cast(
            list[str] | None,
            topic_model.get_representative_docs(
                topic_id
            ),
        ) or []

        representative_text = "\n".join(
            doc
            .replace("\n", " ")
            .replace("\r", " ")
            .strip()[:300]
            for doc
            in representative_docs[:3]
        )

        # -------------------------------------------------
        # Prompt
        # -------------------------------------------------

        categories_text = "\n".join(
            f"- {category}"
            for category
            in CATEGORY_LABELS
        )

        prompt = f"""
You are classifying employee feedback for an HR analytics dashboard.

Choose exactly ONE category from the allowed categories.

Allowed categories:
{categories_text}

Topic keywords:
{keyword_text}

Representative employee reviews:
{representative_text}

Rules:
- Return exactly one category from the allowed list.
- Do not invent a category.
- Do not explain your answer.
- Do not use JSON.
- Do not use markdown.
- Do not add punctuation.

Category:
""".strip()

        category = "Other"

        # -------------------------------------------------
        # Generate classification
        # -------------------------------------------------

        try:

            result = cast(
                list[dict[str, Any]],
                generator(
                    prompt,
                    max_new_tokens=MAX_LABEL_TOKENS,
                    do_sample=False,
                    return_full_text=False,
                ),
            )

            raw_label = str(
                result[0][
                    "generated_text"
                ]
            )

            # -------------------------------------------------
            # Normalize model output
            # -------------------------------------------------

            normalized_label = (
                raw_label
                .strip()
                .replace('"', "")
                .replace("'", "")
                .replace("`", "")
            )

            # Qwen sometimes returns the correct category
            # on the first line and then adds an explanation.
            # Use the first meaningful line before validation.
            first_line = next(
                (
                    line.strip()
                    for line in normalized_label.splitlines()
                    if line.strip()
                ),
                "",
            )

            first_line = re.sub(
                r"\s+",
                " ",
                first_line,
            ).strip(" .,:;-")

            normalized_key = first_line.lower()

            if normalized_key in category_lookup:
                category = category_lookup[normalized_key]
            else:
                # Fallback: accept an allowed category only
                # when it is the prefix of the generation.
                full_text = re.sub(
                    r"\s+",
                    " ",
                    normalized_label,
                ).strip(" .,:;-").lower()

                matched_category = None

                for allowed in sorted(
                    CATEGORY_LABELS,
                    key=len,
                    reverse=True,
                ):
                    allowed_key = allowed.lower()

                    if full_text == allowed_key:
                        matched_category = allowed
                        break

                    if full_text.startswith(allowed_key):
                        remainder = full_text[len(allowed_key):]

                        if (
                            not remainder
                            or remainder[0].isspace()
                            or remainder[0] in ".:,-;()"
                        ):
                            matched_category = allowed
                            break

                if matched_category is not None:
                    category = matched_category
                else:
                    logging.warning(
                        "Invalid category from LLM "
                        "for topic %d: %r. "
                        "Using Other.",
                        topic_id,
                        raw_label,
                    )
                    category = "Other"

        except Exception:

            logging.exception(
                "Failed classifying topic %d",
                topic_id,
            )

            category = "Other"

        topic_categories.append(
            category
        )

        logging.info(
            "Topic %d -> %s",
            topic_id,
            category,
        )

    # -------------------------------------------------
    # Store category
    # -------------------------------------------------

    topic_summary = (
        topic_summary.copy()
    )

    topic_summary[
        "topic_category"
    ] = topic_categories

    logging.info(
        "Generated categories for %d topics.",
        len(topic_summary),
    )

    return topic_summary


# =====================================================
# ADD TOPIC CATEGORIES TO REVIEW DATASET
# =====================================================

def add_topic_categories(
    df: pd.DataFrame,
    topic_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Map topic-level business categories back to every
    individual employee review.

    Parameters
    ----------
    df : pd.DataFrame
        Review-level dataframe containing topic_id.

    topic_summary : pd.DataFrame
        Topic-level dataframe containing topic_id and
        topic_category.

    Returns
    -------
    pd.DataFrame
        Review-level dataframe with topic_category.
    """

    logging.info(
        "Mapping topic categories to reviews..."
    )

    df = df.copy()

    # -------------------------------------------------
    # Validate required columns
    # -------------------------------------------------

    required_columns = {
        "topic_id",
        "topic_category",
    }

    missing_columns = (
        required_columns
        - set(topic_summary.columns)
    )

    if missing_columns:

        raise ValueError(
            "topic_summary is missing required "
            f"columns: {sorted(missing_columns)}"
        )

    if "topic_id" not in df.columns:

        raise ValueError(
            "df is missing required column: "
            "topic_id"
        )

    # -------------------------------------------------
    # Build mapping
    # -------------------------------------------------

    category_mapping = dict(
        zip(
            topic_summary[
                "topic_id"
            ].astype(int),
            topic_summary[
                "topic_category"
            ],
        )
    )

    # -------------------------------------------------
    # Map category to every review
    # -------------------------------------------------

    df["topic_category"] = (
        df["topic_id"]
        .map(category_mapping)
        .fillna("Other")
    )

    logging.info(
        "Mapped topic categories to %d reviews.",
        len(df),
    )

    return df


# =====================================================
# DATASET SUMMARY
# =====================================================

def dataset_summary(
    df: pd.DataFrame,
    topic_summary: pd.DataFrame,
) -> None:
    """
    Display basic statistics for the topic modeling
    results.
    """

    logging.info(
        "Dataset Summary"
    )

    # -------------------------------------------------
    # Shape
    # -------------------------------------------------

    print("\nShape:")
    print(
        df.shape
    )

    # -------------------------------------------------
    # Number of topics
    # -------------------------------------------------

    print(
        "\nNumber of Topics:"
    )

    number_of_topics = (
        topic_summary[
            topic_summary[
                "topic_id"
            ] != -1
        ]
        .shape[0]
    )

    print(
        number_of_topics
    )

    # -------------------------------------------------
    # Outliers
    # -------------------------------------------------

    print(
        "\nOutlier Reviews:"
    )

    outlier_count = (
        df["topic_id"] == -1
    ).sum()

    print(
        outlier_count
    )

    # -------------------------------------------------
    # Topic distribution
    # -------------------------------------------------

    print(
        "\nTopic Distribution:"
    )

    print(
        df["topic_id"]
        .value_counts()
        .sort_index()
    )

    # -------------------------------------------------
    # Category distribution
    # -------------------------------------------------

    if (
        "topic_category"
        in df.columns
    ):

        print(
            "\nTopic Category Distribution:"
        )

        print(
            df["topic_category"]
            .value_counts()
        )

    # -------------------------------------------------
    # Top topics
    # -------------------------------------------------

    print(
        "\nTop 10 Topics:"
    )

    display_columns = [
        "topic_id",
        "document_count",
    ]

    if (
        "representative_words"
        in topic_summary.columns
    ):

        display_columns.append(
            "representative_words"
        )

    if (
        "topic_category"
        in topic_summary.columns
    ):

        display_columns.append(
            "topic_category"
        )

    top_topics = (
        topic_summary[
            topic_summary[
                "topic_id"
            ] != -1
        ]
        .sort_values(
            "document_count",
            ascending=False,
        )
        [display_columns]
        .head(10)
    )

    print(
        top_topics
    )

    # -------------------------------------------------
    # Average probability
    # -------------------------------------------------

    print(
        "\nAverage Topic Probability:"
    )

    valid_probabilities = (
        df["topic_probability"]
        .dropna()
    )

    if len(valid_probabilities) > 0:

        print(
            round(
                valid_probabilities.mean(),
                4,
            )
        )

    else:

        print(
            "N/A"
        )

    # -------------------------------------------------
    # Probability coverage
    # -------------------------------------------------

    print(
        "\nTopic Probability Coverage:"
    )

    probability_count = (
        df["topic_probability"]
        .notna()
        .sum()
    )

    probability_percentage = (
        probability_count
        / len(df)
        * 100
        if len(df) > 0
        else 0
    )

    print(
        f"{probability_count:,} / "
        f"{len(df):,} "
        f"({probability_percentage:.2f}%)"
    )

# =====================================================
# PREVIEW DATASET
# =====================================================

def preview_dataset(
    df: pd.DataFrame,
    rows: int = 5,
) -> None:
    """
    Display sample topic assignments.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset after topic modeling.

    rows : int, default=5
        Number of rows to display.
    """

    logging.info(
        "Previewing topic assignments..."
    )

    columns = [
        "topic_text",
        "sentiment",
        "topic_id",
        "topic_name",
        "topic_category",
        "topic_keywords",
        "topic_probability",
    ]

    print()

    print(
        df[columns]
        .head(rows)
    )

# =====================================================
# SAVE DATASET
# =====================================================

def save_dataset(
    df: pd.DataFrame,
    output_path: Path = OUTPUT_FILE,
) -> None:
    """
    Save the topic modeling dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset after topic modeling.

    output_path : Path, default=OUTPUT_FILE
        Output CSV file.
    """

    logging.info(
        "Saving topic modeling dataset..."
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
# SAVE TOPIC INFORMATION
# =====================================================

def save_topic_information(
    topic_summary: pd.DataFrame,
    output_path: Path = TOPIC_INFO_FILE,
) -> None:
    """
    Save topic summary information.

    Parameters
    ----------
    topic_summary : pd.DataFrame
        Simplified topic information.

    output_path : Path, default=TOPIC_INFO_FILE
        Output CSV file.
    """

    logging.info(
        "Saving topic information..."
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    topic_summary.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    logging.info(
        f"Topic information saved to:\n"
        f"{output_path}"
    )


# =====================================================
# SAVE BERTopic MODEL
# =====================================================

def save_model(
    topic_model: BERTopic,
    output_dir: Path = MODEL_OUTPUT_DIR,
) -> None:
    """
    Save the trained BERTopic model.

    Parameters
    ----------
    topic_model : BERTopic
        Trained BERTopic model.

    output_dir : Path
        Directory where the model will be saved.
    """

    logging.info(
        "Saving BERTopic model..."
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    topic_model.save(
        output_dir,
        serialization="safetensors",
        save_ctfidf=True,
        save_embedding_model=EMBEDDING_MODEL_NAME,
    )

    logging.info(
        f"Model saved to:\n{output_dir}"
    )


# =====================================================
# SAVE TOPIC DISTRIBUTION FIGURE
# =====================================================

def save_topic_distribution(
    topic_summary: pd.DataFrame,
    output_path: Path = (
        TOPIC_DISTRIBUTION_FIGURE
    ),
) -> None:
    """
    Generate and save a topic distribution chart.

    Parameters
    ----------
    topic_summary : pd.DataFrame
        Topic summary.

    output_path : Path
        Output PNG path.
    """

    logging.info(
        "Generating topic distribution figure..."
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plot_data = (

        topic_summary

        .query(
            "topic_id != -1"
        )

        .nlargest(
            15,
            "document_count",
        )

    )

    plt.figure(
        figsize=(12, 6)
    )

    plt.barh(

        plot_data["topic_name"],

        plot_data["document_count"],

    )

    plt.xlabel(
        "Number of Reviews"
    )

    plt.ylabel(
        "Topic"
    )

    plt.title(
        "Top 15 Topic Distribution"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    logging.info(
        f"Figure saved to:\n{output_path}"
    )


# =====================================================
# SAVE INTERACTIVE VISUALIZATION
# =====================================================

def save_topic_visualization(
    topic_model: BERTopic,
    output_path: Path = (
        TOPIC_VISUALIZATION_FILE
    ),
) -> None:
    """
    Save BERTopic interactive visualization.

    Parameters
    ----------
    topic_model : BERTopic
        Trained BERTopic model.

    output_path : Path
        Output HTML path.
    """

    logging.info(
        "Generating interactive visualization..."
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure = (
        topic_model.visualize_topics()
    )

    figure.write_html(
        str(output_path)
    )

    logging.info(
        f"Visualization saved to:\n"
        f"{output_path}"
    )


# =====================================================
# FUTURE VISUALIZATIONS
# =====================================================

def save_topic_barchart(
    topic_model: BERTopic,
) -> None:
    """
    Placeholder for BERTopic bar chart visualization.

    This visualization will be implemented during the
    dashboard development phase.
    """

    pass


def save_topic_heatmap(
    topic_model: BERTopic,
) -> None:
    """
    Placeholder for BERTopic heatmap visualization.

    This visualization will be implemented during the
    dashboard development phase.
    """

    pass


def save_topic_hierarchy(
    topic_model: BERTopic,
) -> None:
    """
    Placeholder for BERTopic hierarchy visualization.

    This visualization will be implemented during the
    dashboard development phase.
    """

    pass


def save_document_visualization(
    topic_model: BERTopic,
) -> None:
    """
    Placeholder for BERTopic document visualization.

    This visualization will be implemented during the
    dashboard development phase.
    """

    pass


# =====================================================
# TOPIC MODELING PIPELINE
# =====================================================

def topic_modeling_pipeline(
    input_path: Path = INPUT_FILE,
) -> pd.DataFrame:
    """
    Complete BERTopic modeling pipeline.

    Workflow

    Load Dataset
        ↓
    Train BERTopic
        ↓
    Generate Topic Summary
        ↓
    Dataset Summary
        ↓
    Preview Dataset
        ↓
    Save Dataset
        ↓
    Save Topic Information
        ↓
    Save BERTopic Model
        ↓
    Save Topic Distribution
        ↓
    Save Interactive Visualization

    Parameters
    ----------
    input_path : Path, default=INPUT_FILE
        Input dataset.

    Returns
    -------
    pd.DataFrame
        Dataset with assigned topics.
    """

    logging.info("=" * 60)

    logging.info(
        "Starting topic modeling pipeline"
    )

    logging.info("=" * 60)

    # -------------------------------------------------
    # Load dataset
    # -------------------------------------------------

    df = load_dataset(
        input_path
    )

    if df.empty:

        logging.warning(
            "Dataset is empty."
        )

        logging.warning(
            "Topic modeling aborted."
        )

        return df

    # -------------------------------------------------
    # Train BERTopic
    # -------------------------------------------------

    (
        df,
        topic_model,
        topic_info,
    ) = train_topic_model(
        df
    )

    # -------------------------------------------------
    # Generate topic summary
    # -------------------------------------------------

    topic_summary = (
        generate_topic_summary(
            topic_info
        )
    )

    # -------------------------------------------------
    # Generate controlled business categories
    # -------------------------------------------------

    topic_summary = generate_topic_labels(
        topic_model,
        topic_summary,
    )

    # -------------------------------------------------
    # Map categories to reviews
    # -------------------------------------------------

    df = add_topic_categories(
        df,
        topic_summary,
    )

    # -------------------------------------------------
    # Display results
    # -------------------------------------------------

    dataset_summary(
        df,
        topic_summary,
    )

    preview_dataset(
        df
    )

    # -------------------------------------------------
    # Save outputs
    # -------------------------------------------------

    save_dataset(
        df
    )

    save_topic_information(
        topic_summary
    )

    save_model(
        topic_model
    )

    save_topic_distribution(
        topic_summary
    )

    save_topic_visualization(
        topic_model
    )

    # -------------------------------------------------
    # Future dashboard visualizations
    # -------------------------------------------------

    # save_topic_barchart(topic_model)
    # save_topic_heatmap(topic_model)
    # save_topic_hierarchy(topic_model)
    # save_document_visualization(topic_model)

    logging.info("=" * 60)

    logging.info(
        "Topic modeling completed successfully."
    )

    logging.info("=" * 60)

    return df


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Entry point when running this module directly.
    """

    topic_modeling_pipeline()


if __name__ == "__main__":
    main()