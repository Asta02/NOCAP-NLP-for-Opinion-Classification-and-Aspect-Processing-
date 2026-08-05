"""Compare sentiment_label, sentiment, and overall_rating."""

from pathlib import Path
import logging

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    cohen_kappa_score,
    ConfusionMatrixDisplay,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "sentiment_reviews.csv"

OUTPUT_DIR = BASE_DIR / "data" / "evaluation" / "comparison"

LABELS = ["Negative", "Neutral", "Positive"]


def rating_to_sentiment(rating):
    if rating in (1, 2):
        return "Negative"
    elif rating == 3:
        return "Neutral"
    elif rating in (4, 5):
        return "Positive"
    else:
        return None


def evaluate(df, truth_col, pred_col, name):
    """Evaluate one pair of sentiment columns."""

    evaluation_df = df[[truth_col, pred_col]].dropna().copy()

    evaluation_df[truth_col] = (
        evaluation_df[truth_col]
        .astype(str)
        .str.strip()
        .str.title()
    )

    evaluation_df[pred_col] = (
        evaluation_df[pred_col]
        .astype(str)
        .str.strip()
        .str.title()
    )

    evaluation_df = evaluation_df[
        evaluation_df[truth_col].isin(LABELS)
        & evaluation_df[pred_col].isin(LABELS)
    ]

    y_true = evaluation_df[truth_col]
    y_pred = evaluation_df[pred_col]

    accuracy = accuracy_score(y_true, y_pred)

    macro_precision, macro_recall, macro_f1, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=LABELS,
            average="macro",
            zero_division=0,
        )
    )

    weighted_precision, weighted_recall, weighted_f1, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=LABELS,
            average="weighted",
            zero_division=0,
        )
    )

    kappa = cohen_kappa_score(
        y_true,
        y_pred,
        labels=LABELS,
    )

    summary = pd.DataFrame([
        {
            "comparison": name,
            "samples": len(evaluation_df),
            "accuracy": accuracy,
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
            "macro_f1": macro_f1,
            "weighted_precision": weighted_precision,
            "weighted_recall": weighted_recall,
            "weighted_f1": weighted_f1,
            "cohen_kappa": kappa,
        }
    ])

    report = pd.DataFrame(
        classification_report(
            y_true,
            y_pred,
            labels=LABELS,
            output_dict=True,
            zero_division=0,
        )
    ).transpose()

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS,
    )

    cm_df = pd.DataFrame(
        cm,
        index=[f"Actual_{x}" for x in LABELS],
        columns=[f"Predicted_{x}" for x in LABELS],
    )

    summary.to_csv(
        OUTPUT_DIR / f"{name}_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    report.to_csv(
        OUTPUT_DIR / f"{name}_classification_report.csv",
        encoding="utf-8-sig",
    )

    cm_df.to_csv(
        OUTPUT_DIR / f"{name}_confusion_matrix.csv",
        encoding="utf-8-sig",
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=LABELS,
    )

    fig, ax = plt.subplots(figsize=(6, 5))

    display.plot(
        ax=ax,
        cmap="Blues",
        values_format="d",
        colorbar=False,
    )

    ax.set_title(name.replace("_", " ").title())

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / f"{name}_confusion_matrix.png",
        dpi=300,
    )

    plt.close(fig)

    print("=" * 70)
    print(name.upper())
    print("=" * 70)

    print(summary.to_string(index=False))

    print("\nClassification Report")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=LABELS,
            digits=4,
            zero_division=0,
        )
    )


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    required = [
        "sentiment_label",
        "sentiment",
        "overall_rating",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["rating_sentiment"] = df["overall_rating"].apply(
        rating_to_sentiment
    )

    evaluate(
        df,
        "sentiment_label",
        "sentiment",
        "human_vs_roberta",
    )

    evaluate(
        df,
        "sentiment_label",
        "rating_sentiment",
        "human_vs_rating",
    )

    evaluate(
        df,
        "rating_sentiment",
        "sentiment",
        "rating_vs_roberta",
    )


if __name__ == "__main__":
    main()