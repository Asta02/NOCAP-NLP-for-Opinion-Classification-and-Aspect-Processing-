"""Evaluate RoBERTa sentiment predictions against rating-derived reference labels."""

from pathlib import Path
import logging

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    cohen_kappa_score,
    precision_recall_fscore_support,
    ConfusionMatrixDisplay,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "sentiment_reviews.csv"
OUTPUT_DIR = BASE_DIR / "data" / "evaluation"

SUMMARY_FILE = OUTPUT_DIR / "sentiment_evaluation_summary.csv"
REPORT_FILE = OUTPUT_DIR / "sentiment_classification_report.csv"
CONFUSION_FILE = OUTPUT_DIR / "sentiment_confusion_matrix.csv"
CONFUSION_PLOT_FILE = OUTPUT_DIR / "sentiment_confusion_matrix.png"

LABELS = ["Negative", "Neutral", "Positive"]


def rating_to_sentiment(rating: float) -> str:
    """Convert a 1-5 employee rating into a rating-derived reference label."""
    if rating in (1, 2):
        return "Negative"
    if rating == 3:
        return "Neutral"
    if rating in (4, 5):
        return "Positive"

    raise ValueError(f"Unexpected overall_rating: {rating}")


def main() -> None:
    logging.info("Loading %s", INPUT_FILE)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    required = ["overall_rating", "sentiment"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Keep only rows that can actually be evaluated.
    evaluation_df = df[required].dropna().copy()

    evaluation_df["reference_sentiment"] = (
        evaluation_df["overall_rating"].apply(rating_to_sentiment)
    )

    evaluation_df["sentiment"] = (
        evaluation_df["sentiment"].astype(str).str.strip().str.title()
    )

    # Only evaluate known sentiment labels.
    evaluation_df = evaluation_df[
        evaluation_df["sentiment"].isin(LABELS)
    ].copy()

    y_true = evaluation_df["reference_sentiment"]
    y_pred = evaluation_df["sentiment"]

    # ---------------------------------------------------------
    # Overall metrics
    # ---------------------------------------------------------

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

    kappa = cohen_kappa_score(y_true, y_pred, labels=LABELS)

    # ---------------------------------------------------------
    # Classification report
    # ---------------------------------------------------------

    report_dict = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        output_dict=True,
        zero_division=0,
    )

    report_df = pd.DataFrame(report_dict).transpose()

    # ---------------------------------------------------------
    # Confusion matrix
    # ---------------------------------------------------------

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS,
    )

    cm_df = pd.DataFrame(
        cm,
        index=[f"Actual_{label}" for label in LABELS],
        columns=[f"Predicted_{label}" for label in LABELS],
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    summary_df = pd.DataFrame([
        {"metric": "evaluated_reviews", "value": len(evaluation_df)},
        {"metric": "accuracy", "value": accuracy},
        {"metric": "macro_precision", "value": macro_precision},
        {"metric": "macro_recall", "value": macro_recall},
        {"metric": "macro_f1", "value": macro_f1},
        {"metric": "weighted_precision", "value": weighted_precision},
        {"metric": "weighted_recall", "value": weighted_recall},
        {"metric": "weighted_f1", "value": weighted_f1},
        {"metric": "cohen_kappa", "value": kappa},
    ])

    # ---------------------------------------------------------
    # Save outputs
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(
        SUMMARY_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    report_df.to_csv(
        REPORT_FILE,
        encoding="utf-8-sig",
    )

    cm_df.to_csv(
        CONFUSION_FILE,
        encoding="utf-8-sig",
    )

    # ---------------------------------------------------------
    # Confusion matrix plot
    # ---------------------------------------------------------

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=LABELS,
    )

    fig, ax = plt.subplots(figsize=(7, 6))

    display.plot(
        ax=ax,
        cmap="Blues",
        values_format=",d",
        colorbar=False,
    )

    ax.set_title(
        "RoBERTa Sentiment vs Rating-Derived Reference Labels"
    )

    fig.tight_layout()

    fig.savefig(
        CONFUSION_PLOT_FILE,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    # ---------------------------------------------------------
    # Console output
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("SENTIMENT MODEL EVALUATION")
    print("=" * 60)

    print(f"Evaluated reviews : {len(evaluation_df):,}")
    print(f"Accuracy          : {accuracy:.4f}")
    print(f"Macro Precision   : {macro_precision:.4f}")
    print(f"Macro Recall      : {macro_recall:.4f}")
    print(f"Macro F1          : {macro_f1:.4f}")
    print(f"Weighted F1       : {weighted_f1:.4f}")
    print(f"Cohen's Kappa     : {kappa:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=LABELS,
            digits=4,
            zero_division=0,
        )
    )

    print("Confusion Matrix:")
    print(cm_df.to_string())

    print("\nReference label distribution:")
    print(y_true.value_counts().reindex(LABELS, fill_value=0).to_string())

    print("\nPredicted label distribution:")
    print(y_pred.value_counts().reindex(LABELS, fill_value=0).to_string())

    logging.info("Summary: %s", SUMMARY_FILE)
    logging.info("Classification report: %s", REPORT_FILE)
    logging.info("Confusion matrix: %s", CONFUSION_FILE)
    logging.info("Confusion matrix plot: %s", CONFUSION_PLOT_FILE)


if __name__ == "__main__":
    main()