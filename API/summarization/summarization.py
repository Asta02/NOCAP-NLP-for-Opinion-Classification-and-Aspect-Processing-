"""
=========================================================
Employee Review Topic Summarization Pipeline
=========================================================

Project : NLP for Opinion Classification and Aspect Processing (NO CAP)

Description
-----------
This module summarizes discovered employee-review topics and
their sentiment groups using Qwen/Qwen2.5-1.5B-Instruct.

Input
-----
data/processed/topic_reviews.csv

Output
------
data/processed/topic_summaries.csv

Pipeline
--------
1. Load topic review dataset
2. Validate required columns
3. Clean review text
4. Group reviews by topic
5. Select representative reviews
6. Split topic reviews by sentiment
7. Chunk long review collections safely
8. Generate chunk summaries
9. Reduce chunk summaries into final summaries
10. Build topic-level summary dataset
11. Preview summary statistics
12. Save topic_summaries.csv
"""

from pathlib import Path
import logging
import re
from typing import Any, cast

import pandas as pd
import torch
from transformers.pipelines import pipeline


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

INPUT_FILE = (
    PROCESSED_DATA_DIR
    / "topic_reviews.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "topic_summaries.csv"
)


# =====================================================
# CONSTANTS
# =====================================================

SUMMARIZATION_MODEL = (
    "Qwen/Qwen2.5-1.5B-Instruct"
)

REQUIRED_COLUMNS = {
    "topic_id",
    "topic_category",
    "sentiment",
    "summary_text",
}

SENTIMENT_LABELS = (
    "positive",
    "neutral",
    "negative",
)

MAX_REVIEWS_PER_TOPIC = 40
MAX_REVIEWS_PER_SENTIMENT = 24

# Maximum token budget used for review content inside one
# summarization request. Prompt tokens and generated tokens
# are intentionally kept outside this budget.
MAX_CHUNK_TOKENS = 3000

MAX_SUMMARY_TOKENS = 120
MAX_FINAL_SUMMARY_TOKENS = 160

MIN_REVIEW_CHARACTERS = 20
MAX_REVIEW_CHARACTERS = 1500

# Sentiment-specific summaries are only generated when
# enough reviews exist to support a meaningful synthesis.
MIN_REVIEWS_FOR_SENTIMENT_SUMMARY = 5

EXCLUDE_OUTLIERS = True


# =====================================================
# LOAD SUMMARIZATION MODEL (LAZY LOADING)
# =====================================================

_summarizer = None


def get_summarizer():
    """
    Load the Qwen text-generation pipeline only when it
    is first required.

    Returns
    -------
    transformers.Pipeline
        Loaded text-generation pipeline.
    """

    global _summarizer

    if _summarizer is None:

        logging.info(
            "Loading summarization model..."
        )

        device = (
            0
            if torch.cuda.is_available()
            else -1
        )

        logging.info(
            "Using device: %s",
            "cuda"
            if torch.cuda.is_available()
            else "cpu",
        )

        _summarizer = pipeline(
            task="text-generation",
            model=SUMMARIZATION_MODEL,
            device=device,
            torch_dtype=(
                torch.float16
                if torch.cuda.is_available()
                else None
            ),
            model_kwargs={
                "low_cpu_mem_usage": True,
            },
        )

    return _summarizer


# =====================================================
# LOAD DATASET
# =====================================================

def load_dataset(
    path: Path = INPUT_FILE,
) -> pd.DataFrame:
    """
    Load the topic modeling output dataset.

    Parameters
    ----------
    path : Path, default=INPUT_FILE
        Path to topic_reviews.csv.

    Returns
    -------
    pd.DataFrame
        Loaded review-level dataset.
    """

    logging.info(
        "Loading topic review dataset..."
    )

    df = pd.read_csv(path)

    logging.info(
        "Dataset shape: %s",
        df.shape,
    )

    return df


# =====================================================
# VALIDATE DATASET
# =====================================================

def validate_dataset(
    df: pd.DataFrame,
) -> None:
    """
    Validate columns required by the summarization phase.

    Parameters
    ----------
    df : pd.DataFrame
        Topic review dataset.

    Raises
    ------
    ValueError
        If required columns are missing.
    """

    missing_columns = (
        REQUIRED_COLUMNS
        - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            "Dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )


# =====================================================
# CLEAN REVIEW TEXT
# =====================================================

def clean_review_text(
    text: object,
) -> str:
    """
    Normalize review text before selection and
    summarization.

    Parameters
    ----------
    text : object
        Raw summary_text value.

    Returns
    -------
    str
        Cleaned review text.
    """

    if pd.isna(text):

        return ""

    cleaned = str(text)

    cleaned = (
        cleaned
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("\t", " ")
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    ).strip()

    if len(cleaned) > MAX_REVIEW_CHARACTERS:

        cleaned = (
            cleaned[
                :MAX_REVIEW_CHARACTERS
            ]
            .rsplit(
                " ",
                1,
            )[0]
            .strip()
        )

    return cleaned


# =====================================================
# PREPARE DATASET
# =====================================================

def prepare_dataset(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean fields used by the summarization pipeline.

    Invalid/empty summary_text rows are removed. Sentiment
    labels are normalized to lowercase.

    Parameters
    ----------
    df : pd.DataFrame
        Raw topic review dataset.

    Returns
    -------
    pd.DataFrame
        Cleaned dataset.
    """

    logging.info(
        "Preparing review text..."
    )

    df = df.copy()

    df["topic_id"] = pd.to_numeric(
        df["topic_id"],
        errors="coerce",
    )

    invalid_topic_ids = (
        df["topic_id"]
        .isna()
        .sum()
    )

    if invalid_topic_ids:

        logging.warning(
            "Dropping %d rows with invalid topic_id.",
            invalid_topic_ids,
        )

        df = df[
            df["topic_id"].notna()
        ].copy()

    df["topic_id"] = (
        df["topic_id"]
        .astype(int)
    )

    df["summary_text"] = (
        df["summary_text"]
        .apply(clean_review_text)
    )

    df["sentiment"] = (
        df["sentiment"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["topic_category"] = (
        df["topic_category"]
        .fillna("Other")
        .astype(str)
        .str.strip()
        .replace("", "Other")
    )

    valid_sentiments = set(
        SENTIMENT_LABELS
    )

    unknown_sentiments = (
        ~df["sentiment"]
        .isin(valid_sentiments)
    )

    unknown_count = int(
        unknown_sentiments.sum()
    )

    if unknown_count:

        logging.warning(
            "%d reviews have unsupported sentiment labels. "
            "They will count toward overall summaries but "
            "not positive/neutral/negative summaries.",
            unknown_count,
        )

    before = len(df)

    df = df[
        df["summary_text"]
        .str.len()
        .ge(MIN_REVIEW_CHARACTERS)
    ].copy()

    removed = (
        before
        - len(df)
    )

    logging.info(
        "Removed %d empty/very short reviews.",
        removed,
    )

    if EXCLUDE_OUTLIERS:

        outlier_count = int(
            (df["topic_id"] == -1)
            .sum()
        )

        if outlier_count:

            logging.info(
                "Excluding %d BERTopic outlier reviews.",
                outlier_count,
            )

            df = df[
                df["topic_id"] != -1
            ].copy()

    return df


# =====================================================
# REPRESENTATIVE REVIEW SELECTION
# =====================================================

def _review_quality_score(
    text: str,
) -> float:
    """
    Score a review for usefulness in topic summarization.

    The score favors reviews with enough detail to carry
    information while avoiding a simple dataframe-order
    selection strategy.
    """

    length = len(text)

    # Reviews around 250-700 characters usually contain
    # enough context without being excessively verbose.
    if 250 <= length <= 700:
        length_score = 3.0

    elif 120 <= length < 250:
        length_score = 2.0

    elif 700 < length <= 1000:
        length_score = 2.0

    else:
        length_score = 1.0

    word_count = len(
        text.split()
    )

    detail_score = min(
        word_count / 40.0,
        2.0,
    )

    return (
        length_score
        + detail_score
    )


def _select_from_frame(
    reviews: pd.DataFrame,
    max_reviews: int,
) -> list[str]:
    """
    Select useful, unique reviews from one dataframe.
    """

    if reviews.empty:

        return []

    candidates = (
        reviews[
            ["summary_text"]
        ]
        .copy()
    )

    candidates = candidates[
        candidates["summary_text"]
        .astype(str)
        .str.len()
        .ge(MIN_REVIEW_CHARACTERS)
    ].copy()

    candidates = (
        candidates
        .drop_duplicates(
            subset=["summary_text"]
        )
    )

    candidates["_quality"] = (
        candidates["summary_text"]
        .apply(_review_quality_score)
    )

    # Stable sorting makes selection reproducible while
    # avoiding dependence on arbitrary dataframe order.
    candidates = candidates.sort_values(
        by=[
            "_quality",
            "summary_text",
        ],
        ascending=[
            False,
            True,
        ],
        kind="stable",
    )

    return (
        candidates["summary_text"]
        .head(max_reviews)
        .tolist()
    )


def select_reviews(
    reviews: pd.DataFrame,
    max_reviews: int = MAX_REVIEWS_PER_TOPIC,
) -> list[str]:
    """
    Select representative reviews for summarization.

    When multiple sentiment groups are present, the
    selector reserves capacity across those groups so a
    large majority sentiment does not completely suppress
    minority feedback.

    Parameters
    ----------
    reviews : pd.DataFrame
        Review rows containing summary_text and sentiment.

    max_reviews : int
        Maximum reviews to return.

    Returns
    -------
    list[str]
        Selected review texts.
    """

    if reviews.empty or max_reviews <= 0:

        return []

    reviews = reviews.copy()

    sentiments_present = [
        sentiment
        for sentiment in SENTIMENT_LABELS
        if (
            reviews["sentiment"]
            == sentiment
        ).any()
    ]

    # If this is already a single-sentiment subset, use
    # the full capacity directly.
    if len(sentiments_present) <= 1:

        return _select_from_frame(
            reviews,
            max_reviews,
        )

    selected: list[str] = []

    # Reserve an equal first-pass allocation for each
    # recognized sentiment represented in the topic.
    per_group = max(
        1,
        max_reviews
        // len(sentiments_present),
    )

    for sentiment in sentiments_present:

        subset = reviews[
            reviews["sentiment"]
            == sentiment
        ]

        selected.extend(
            _select_from_frame(
                subset,
                per_group,
            )
        )

    # Fill remaining capacity from all reviews, including
    # any rows with unrecognized sentiment labels.
    if len(selected) < max_reviews:

        selected_set = set(
            selected
        )

        remaining = reviews[
            ~reviews["summary_text"]
            .isin(selected_set)
        ]

        selected.extend(
            _select_from_frame(
                remaining,
                max_reviews
                - len(selected),
            )
        )

    # Preserve order while removing any duplicate text
    # introduced across selection passes.
    return list(
        dict.fromkeys(
            selected
        )
    )[:max_reviews]


# =====================================================
# TOKEN HELPERS
# =====================================================

def _count_tokens(
    text: str,
) -> int:
    """
    Count tokens using the active Qwen tokenizer.
    """

    tokenizer = (
        get_summarizer()
        .tokenizer
    )

    return len(
        tokenizer.encode(
            text,
            add_special_tokens=False,
        )
    )


def _truncate_to_tokens(
    text: str,
    max_tokens: int,
) -> str:
    """
    Truncate text to a tokenizer-aware token limit.
    """

    tokenizer = (
        get_summarizer()
        .tokenizer
    )

    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False,
    )

    if len(token_ids) <= max_tokens:

        return text

    token_ids = (
        token_ids[:max_tokens]
    )

    return tokenizer.decode(
        token_ids,
        skip_special_tokens=True,
    ).strip()


# =====================================================
# CHUNK REVIEWS
# =====================================================

def chunk_reviews(
    reviews: list[str],
    max_tokens: int = MAX_CHUNK_TOKENS,
) -> list[list[str]]:
    """
    Split reviews into tokenizer-aware chunks.

    Individual reviews that exceed the chunk budget are
    truncated safely.

    Parameters
    ----------
    reviews : list[str]
        Review texts.

    max_tokens : int
        Maximum review-content tokens per chunk.

    Returns
    -------
    list[list[str]]
        Review chunks.
    """

    if not reviews:

        return []

    chunks: list[list[str]] = []
    current_chunk: list[str] = []
    current_tokens = 0

    for review in reviews:

        review = review.strip()

        if not review:

            continue

        review_tokens = (
            _count_tokens(review)
            + 8
        )

        if review_tokens > max_tokens:

            review = _truncate_to_tokens(
                review,
                max_tokens - 8,
            )

            review_tokens = (
                _count_tokens(review)
                + 8
            )

        if (
            current_chunk
            and (
                current_tokens
                + review_tokens
                > max_tokens
            )
        ):

            chunks.append(
                current_chunk
            )

            current_chunk = []
            current_tokens = 0

        current_chunk.append(
            review
        )

        current_tokens += (
            review_tokens
        )

    if current_chunk:

        chunks.append(
            current_chunk
        )

    return chunks


# =====================================================
# GENERATION HELPER
# =====================================================

def _generate_text(
    prompt: str,
    max_new_tokens: int,
) -> str:
    """
    Generate deterministic text with Qwen.
    """

    generator = get_summarizer()

    with torch.inference_mode():
        result = cast(
            list[dict[str, Any]],
            generator(
                prompt,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                return_full_text=False,
            ),
        )

    generated_text = str(
        result[0][
            "generated_text"
        ]
    ).strip()

    generated_text = re.sub(
        r"\s+",
        " ",
        generated_text,
    ).strip()

    return generated_text


# =====================================================
# SUMMARIZE ONE CHUNK
# =====================================================

def summarize_chunk(
    reviews: list[str],
    topic_category: str,
    sentiment: str | None = None,
) -> str:
    """
    Summarize one chunk of employee reviews.
    """

    if not reviews:

        return ""

    review_text = "\n".join(
        f"- {review}"
        for review in reviews
    )

    if sentiment is None:

        scope = (
            "all sentiment groups"
        )

    else:

        scope = (
            f"{sentiment} reviews only"
        )

    prompt = f"""
You summarize employee feedback for an HR analytics system.

Topic category:
{topic_category}

Scope:
{scope}

Employee reviews:
{review_text}

Instructions:
- Summarize only information supported by the reviews.
- Identify recurring employee feedback, not isolated speculation.
- Preserve important nuance and mixed opinions.
- Do not invent facts, causes, statistics, policies, or recommendations.
- Do not give management advice or HR actions.
- Do not produce key strengths, key issues, or recommendations.
- Do not mention that you are an AI.
- Write one concise paragraph in neutral analytical language.
- Focus on what employees are saying.

Summary:
""".strip()

    return _generate_text(
        prompt,
        MAX_SUMMARY_TOKENS,
    )


# =====================================================
# REDUCE CHUNK SUMMARIES
# =====================================================

def reduce_summaries(
    summaries: list[str],
    topic_category: str,
    sentiment: str | None = None,
) -> str:
    """
    Combine intermediate summaries into one final summary.

    Reduction is recursive when the intermediate summaries
    are too large for one prompt.
    """

    summaries = [
        summary.strip()
        for summary in summaries
        if summary.strip()
    ]

    if not summaries:

        return ""

    if len(summaries) == 1:

        return summaries[0]

    summary_chunks = chunk_reviews(
        summaries,
        max_tokens=MAX_CHUNK_TOKENS,
    )

    reduced: list[str] = []

    for chunk in summary_chunks:

        summary_text = "\n".join(
            f"- {summary}"
            for summary in chunk
        )

        if sentiment is None:

            scope = (
                "all sentiment groups"
            )

        else:

            scope = (
                f"{sentiment} reviews only"
            )

        prompt = f"""
You are combining partial summaries of employee feedback.

Topic category:
{topic_category}

Scope:
{scope}

Partial summaries:
{summary_text}

Instructions:
- Merge overlapping points and remove repetition.
- Keep only claims supported by the partial summaries.
- Preserve recurring patterns and important nuance.
- Do not invent facts, causes, statistics, or recommendations.
- Do not give management advice or HR actions.
- Write one concise paragraph in neutral analytical language.
- Describe what employees are saying.

Final summary:
""".strip()

        reduced.append(
            _generate_text(
                prompt,
                MAX_FINAL_SUMMARY_TOKENS,
            )
        )

    if len(reduced) == 1:

        return reduced[0]

    # Continue reducing until one final summary remains.
    return reduce_summaries(
        reduced,
        topic_category=topic_category,
        sentiment=sentiment,
    )


# =====================================================
# SUMMARIZE REVIEW COLLECTION
# =====================================================

def summarize_reviews(
    reviews: list[str],
    topic_category: str,
    sentiment: str | None = None,
) -> str:
    """
    Chunk and summarize a selected review collection.

    Parameters
    ----------
    reviews : list[str]
        Selected review texts.

    topic_category : str
        Controlled topic category.

    sentiment : str | None
        Optional sentiment scope.

    Returns
    -------
    str
        Final synthesized summary.
    """

    if not reviews:

        return ""

    chunks = chunk_reviews(
        reviews
    )

    logging.info(
        "Summarizing %d reviews in %d chunk(s).",
        len(reviews),
        len(chunks),
    )

    chunk_summaries: list[str] = []

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        logging.info(
            "Generating chunk summary %d/%d...",
            index,
            len(chunks),
        )

        try:

            summary = summarize_chunk(
                chunk,
                topic_category=topic_category,
                sentiment=sentiment,
            )

        except Exception:

            logging.exception(
                "Failed to summarize chunk %d/%d.",
                index,
                len(chunks),
            )

            continue

        if summary:

            chunk_summaries.append(
                summary
            )

    if not chunk_summaries:

        return ""

    try:

        return reduce_summaries(
            chunk_summaries,
            topic_category=topic_category,
            sentiment=sentiment,
        )

    except Exception:

        logging.exception(
            "Failed to reduce chunk summaries."
        )

        # A partial summary is preferable to inventing or
        # silently discarding all successfully generated
        # information.
        return " ".join(
            chunk_summaries
        ).strip()


# =====================================================
# TOPIC CATEGORY RESOLUTION
# =====================================================

def get_topic_category(
    topic_df: pd.DataFrame,
) -> str:
    """
    Resolve the topic category for one topic.

    Topic modeling should map one category to every review
    in a topic. If inconsistent values are found, the most
    frequent category is used and a warning is logged.
    """

    categories = (
        topic_df["topic_category"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    categories = categories[
        categories != ""
    ]

    if categories.empty:

        return "Other"

    counts = (
        categories
        .value_counts()
    )

    if len(counts) > 1:

        logging.warning(
            "Topic %s contains multiple topic categories: "
            "%s. Using the most frequent category.",
            topic_df["topic_id"].iloc[0],
            counts.to_dict(),
        )

    return str(
        counts.index[0]
    )


# =====================================================
# SUMMARIZE ONE TOPIC
# =====================================================

def summarize_topic(
    topic_df: pd.DataFrame,
) -> dict[str, object]:
    """
    Generate overall and sentiment-specific summaries for
    one discovered topic.

    Parameters
    ----------
    topic_df : pd.DataFrame
        All review rows assigned to one topic.

    Returns
    -------
    dict[str, object]
        Topic-level summary record.
    """

    topic_id = int(
        topic_df["topic_id"]
        .iloc[0]
    )

    topic_category = (
        get_topic_category(
            topic_df
        )
    )

    document_count = len(
        topic_df
    )

    sentiment_counts = (
        topic_df["sentiment"]
        .value_counts()
    )

    positive_count = int(
        sentiment_counts.get(
            "positive",
            0,
        )
    )

    neutral_count = int(
        sentiment_counts.get(
            "neutral",
            0,
        )
    )

    negative_count = int(
        sentiment_counts.get(
            "negative",
            0,
        )
    )

    logging.info(
        "Topic %d (%s): %d reviews.",
        topic_id,
        topic_category,
        document_count,
    )

    # -------------------------------------------------
    # Overall summary
    # -------------------------------------------------

    overall_reviews = select_reviews(
        topic_df,
        max_reviews=MAX_REVIEWS_PER_TOPIC,
    )

    overall_summary = summarize_reviews(
        overall_reviews,
        topic_category=topic_category,
        sentiment=None,
    )

    # -------------------------------------------------
    # Sentiment summaries
    # -------------------------------------------------

    sentiment_summaries: dict[
        str,
        str,
    ] = {}

    for sentiment in SENTIMENT_LABELS:

        sentiment_df = topic_df[
            topic_df["sentiment"]
            == sentiment
        ]

        if (
            len(sentiment_df)
            < MIN_REVIEWS_FOR_SENTIMENT_SUMMARY
        ):

            logging.info(
                "Topic %d: skipping %s summary "
                "(%d reviews; minimum=%d).",
                topic_id,
                sentiment,
                len(sentiment_df),
                MIN_REVIEWS_FOR_SENTIMENT_SUMMARY,
            )

            sentiment_summaries[
                sentiment
            ] = ""

            continue

        selected_reviews = select_reviews(
            sentiment_df,
            max_reviews=MAX_REVIEWS_PER_SENTIMENT,
        )

        sentiment_summaries[
            sentiment
        ] = summarize_reviews(
            selected_reviews,
            topic_category=topic_category,
            sentiment=sentiment,
        )

    return {
        "topic_id":
            topic_id,
        "topic_category":
            topic_category,
        "document_count":
            document_count,
        "positive_count":
            positive_count,
        "neutral_count":
            neutral_count,
        "negative_count":
            negative_count,
        "overall_summary":
            overall_summary,
        "positive_summary":
            sentiment_summaries[
                "positive"
            ],
        "neutral_summary":
            sentiment_summaries[
                "neutral"
            ],
        "negative_summary":
            sentiment_summaries[
                "negative"
            ],
    }


# =====================================================
# GENERATE TOPIC SUMMARIES
# =====================================================

def generate_topic_summaries(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate one summary row per discovered topic.

    Parameters
    ----------
    df : pd.DataFrame
        Prepared review-level dataset.

    Returns
    -------
    pd.DataFrame
        Topic-level summaries.
    """

    logging.info(
        "Generating topic summaries..."
    )

    output_columns = [
        "topic_id",
        "topic_category",
        "document_count",
        "positive_count",
        "neutral_count",
        "negative_count",
        "overall_summary",
        "positive_summary",
        "neutral_summary",
        "negative_summary",
    ]

    if df.empty:

        return pd.DataFrame(
            columns=output_columns
        )

    records: list[
        dict[str, object]
    ] = []

    grouped = df.groupby(
        "topic_id",
        sort=True,
    )

    total_topics = (
        grouped.ngroups
    )

    for index, (
        topic_id,
        topic_df,
    ) in enumerate(
        grouped,
        start=1,
    ):

        logging.info(
            "Processing topic %s (%d/%d)...",
            topic_id,
            index,
            total_topics,
        )

        try:

            record = summarize_topic(
                topic_df
            )

        except Exception:

            logging.exception(
                "Failed summarizing topic %s.",
                topic_id,
            )

            continue

        records.append(
            record
        )

    summaries = pd.DataFrame(
        records,
        columns=output_columns,
    )

    if not summaries.empty:

        summaries = (
            summaries
            .sort_values(
                "topic_id"
            )
            .reset_index(
                drop=True
            )
        )

    logging.info(
        "Generated summaries for %d topics.",
        len(summaries),
    )

    return summaries


# =====================================================
# PREVIEW STATISTICS
# =====================================================

def preview_statistics(
    summaries: pd.DataFrame,
) -> None:
    """
    Display basic statistics for generated summaries.
    """

    logging.info(
        "Summarization Statistics"
    )

    print(
        "\nShape:"
    )

    print(
        summaries.shape
    )

    if summaries.empty:

        print(
            "\nNo topic summaries generated."
        )

        return

    print(
        "\nTopics Summarized:"
    )

    print(
        len(summaries)
    )

    print(
        "\nTotal Reviews Represented:"
    )

    print(
        int(
            summaries[
                "document_count"
            ].sum()
        )
    )

    print(
        "\nSentiment Counts:"
    )

    print(
        summaries[
            [
                "positive_count",
                "neutral_count",
                "negative_count",
            ]
        ]
        .sum()
    )

    print(
        "\nSummary Coverage:"
    )

    for column in [
        "overall_summary",
        "positive_summary",
        "neutral_summary",
        "negative_summary",
    ]:

        coverage = (
            summaries[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .sum()
        )

        print(
            f"{column}: "
            f"{coverage}/{len(summaries)}"
        )

    print(
        "\nPreview:"
    )

    preview_columns = [
        "topic_id",
        "topic_category",
        "document_count",
        "positive_count",
        "neutral_count",
        "negative_count",
        "overall_summary",
    ]

    with pd.option_context(
        "display.max_colwidth",
        120,
    ):

        print(
            summaries[
                preview_columns
            ]
            .head(10)
        )


# =====================================================
# SAVE DATASET
# =====================================================

def save_dataset(
    summaries: pd.DataFrame,
    output_path: Path = OUTPUT_FILE,
) -> None:
    """
    Save topic summaries to CSV.
    """

    logging.info(
        "Saving topic summaries..."
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summaries.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    logging.info(
        "Topic summaries saved to:\n%s",
        output_path,
    )


# =====================================================
# SUMMARIZATION PIPELINE
# =====================================================

def summarization_pipeline(
    input_path: Path = INPUT_FILE,
    output_path: Path = OUTPUT_FILE,
) -> pd.DataFrame:
    """
    Complete topic summarization pipeline.

    Workflow

    Load topic_reviews.csv
        ↓
    Validate required columns
        ↓
    Clean summary_text
        ↓
    Group by topic_id
        ↓
    Select representative reviews
        ↓
    Split by sentiment
        ↓
    Chunk reviews
        ↓
    Generate chunk summaries
        ↓
    Reduce summaries
        ↓
    Build topic_summaries DataFrame
        ↓
    Preview statistics
        ↓
    Save topic_summaries.csv

    Parameters
    ----------
    input_path : Path
        Input topic review dataset.

    output_path : Path
        Output topic summary dataset.

    Returns
    -------
    pd.DataFrame
        Generated topic summaries.
    """

    logging.info(
        "=" * 60
    )

    logging.info(
        "Starting summarization pipeline"
    )

    logging.info(
        "=" * 60
    )

    df = load_dataset(
        input_path
    )

    if df.empty:

        logging.warning(
            "Dataset is empty."
        )

        empty_output = pd.DataFrame(
            columns=[
                "topic_id",
                "topic_category",
                "document_count",
                "positive_count",
                "neutral_count",
                "negative_count",
                "overall_summary",
                "positive_summary",
                "neutral_summary",
                "negative_summary",
            ]
        )

        save_dataset(
            empty_output,
            output_path,
        )

        return empty_output

    validate_dataset(
        df
    )

    df = prepare_dataset(
        df
    )

    if df.empty:

        logging.warning(
            "No valid reviews remain after preparation."
        )

    summaries = (
        generate_topic_summaries(
            df
        )
    )

    preview_statistics(
        summaries
    )

    save_dataset(
        summaries,
        output_path,
    )

    logging.info(
        "=" * 60
    )

    logging.info(
        "Summarization completed successfully."
    )

    logging.info(
        "=" * 60
    )

    return summaries


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Entry point when running this module directly.
    """

    summarization_pipeline()


if __name__ == "__main__":
    main()
