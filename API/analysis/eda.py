from pathlib import Path
import logging

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "preprocessed_reviews.csv"
)

def load_processed_dataset(path: Path = PROCESSED_FILE):
    df = pd.read_csv(path)
    return df

df = load_processed_dataset()


# =====================================================
# Dataset Overview
# =====================================================
def dataset_overview(df: pd.DataFrame) -> None:
    """
    Display general information about the dataset.
    """

    logging.info("Dataset Overview")

    print(f"Total Reviews : {len(df)}")
    print(f"Total Columns : {len(df.columns)}")

    print("\nMissing Values")
    print(df.isnull().sum())

    print("\nDuplicate Reviews")
    print(df.duplicated().sum())

# =====================================================
# Rating Statistics
# =====================================================
RATING_COLUMNS = [
    "overall_rating",
    "work_life_balance",
    "culture_values",
    "career_opportunities",
    "compensation_benefits",
    "senior_management"
]


def rating_statistics(df: pd.DataFrame) -> None:
    """
    Display descriptive statistics for rating columns.
    """

    logging.info("Rating Statistics")

    print(df[RATING_COLUMNS].describe())

# =====================================================
# Rating Distribution
# =====================================================
FIGURE_DIR = BASE_DIR / "analysis" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)



def rating_distribution(df: pd.DataFrame) -> None:
    """
    Plot overall rating distribution.
    """

    logging.info("Generating rating distribution...")

    counts = (
        df["overall_rating"]
        .value_counts()
        .sort_index()
    )

    plt.figure(figsize=(7,5))
    counts.plot(kind="bar")

    plt.title("Overall Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Number of Reviews")

    plt.tight_layout()

    plt.savefig(FIGURE_DIR / "rating_distribution.png")

    plt.close()

# =====================================================
# Job Title Analysis
# =====================================================
def top_job_titles(df: pd.DataFrame, top_n: int = 10) -> None:
    """
    Display and plot the most common job titles.
    """

    logging.info("Analyzing job titles...")

    jobs = df["job_title"].value_counts().head(top_n)

    print(jobs)

    plt.figure(figsize=(10,6))

    jobs.sort_values().plot(kind="barh")

    plt.title("Top Job Titles")

    plt.tight_layout()

    plt.savefig(FIGURE_DIR / "top_job_titles.png")

    plt.close()

# =====================================================
# Review Trend
# =====================================================
def review_trend(df: pd.DataFrame) -> None:
    """
    Plot review counts by year.
    """

    logging.info("Generating review trend...")

    df["date"] = pd.to_datetime(df["date"])

    trend = (
        df
        .groupby(df["date"].dt.year)
        .size()
    )

    plt.figure(figsize=(8,5))

    trend.plot(marker="o")

    plt.title("Employee Reviews by Year")

    plt.xlabel("Year")
    plt.ylabel("Reviews")

    plt.tight_layout()

    plt.savefig(FIGURE_DIR / "review_trend.png")

    plt.close()

# =====================================================
# Review Length
# =====================================================
def review_length(df: pd.DataFrame) -> None:
    """
    Analyze review length.
    """

    logging.info("Analyzing review length...")

    df["review_length"] = (
        df["processed_text"]
        .str.split()
        .str.len()
    )

    print(df["review_length"].describe())

    plt.figure(figsize=(8,5))

    plt.hist(
        df["review_length"],
        bins=40
    )

    plt.title("Review Length Distribution")

    plt.xlabel("Words")

    plt.ylabel("Frequency")

    plt.tight_layout()

    plt.savefig(FIGURE_DIR / "review_length.png")

    plt.close()

# =====================================================
# Top Words
# =====================================================
from collections import Counter


def top_words(df: pd.DataFrame, top_n: int = 20) -> None:
    """
    Display the most frequent words.
    """
    
    logging.info("Finding top words...")

    words = " ".join(
        df["processed_text"].dropna()
    ).split()

    counter = Counter(words)

    common = counter.most_common(top_n)

    word_df = pd.DataFrame(common, columns=["Word", "Frequency"])

    print(word_df)

    plt.figure(figsize=(10, 6))
    plt.bar(word_df["Word"], word_df["Frequency"])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "top_words.png")
    plt.close()

# =====================================================
# Correlation Heatmap
# =====================================================
def correlation_heatmap(df: pd.DataFrame) -> None:
    """
    Generate correlation heatmap.
    """

    logging.info("Generating correlation heatmap...")

    corr = df[RATING_COLUMNS].corr()

    plt.figure(figsize=(8,6))

    plt.imshow(corr)

    labels = corr.columns.tolist()

    plt.xticks(
        range(len(labels)),
        labels,
        rotation=45,
        ha="right"
    )

    plt.yticks(
        range(len(labels)),
        labels
    )

    plt.colorbar()

    plt.tight_layout()

    plt.savefig(FIGURE_DIR / "correlation_heatmap.png")

    plt.close()

# =====================================================
# Main
# =====================================================
def main():

    df = load_processed_dataset()

    dataset_overview(df)

    rating_statistics(df)

    rating_distribution(df)

    top_job_titles(df)

    review_trend(df)

    review_length(df)

    top_words(df)

    correlation_heatmap(df)


if __name__ == "__main__":
    main()