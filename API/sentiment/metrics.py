"""
=========================================================
Evaluation Metrics
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing (NO CAP)

Description
-----------
Shared evaluation metrics used by both training and
final model evaluation.

Responsibilities
----------------
1. Compute evaluation metrics
2. Generate classification report
3. Generate confusion matrix
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from transformers.trainer_utils import (
    EvalPrediction,
)

from .dataset import ID2LABEL


# =====================================================
# LABELS
# =====================================================

LABEL_IDS = sorted(
    ID2LABEL.keys()
)

TARGET_NAMES = [
    ID2LABEL[label_id]
    for label_id in LABEL_IDS
]

LABEL_MAP = ID2LABEL


# =====================================================
# INTERNAL METRICS
# =====================================================

def _calculate_metrics(
    labels: np.ndarray,
    predictions: np.ndarray,
) -> dict[str, float]:
    """
    Compute evaluation metrics from
    prediction and label arrays.
    """

    precision_macro, recall_macro, f1_macro, _ = (
        precision_recall_fscore_support(
            labels,
            predictions,
            average="macro",
            zero_division=0,
        )
    )

    _, _, f1_weighted, _ = (
        precision_recall_fscore_support(
            labels,
            predictions,
            average="weighted",
            zero_division=0,
        )
    )

    accuracy = accuracy_score(
        labels,
        predictions,
    )

    kappa = cohen_kappa_score(
        labels,
        predictions,
    )

    return {
        "accuracy": accuracy,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "kappa": kappa,
    }


# =====================================================
# HUGGING FACE TRAINER METRICS
# =====================================================

def compute_metrics(
    eval_prediction: EvalPrediction,
) -> dict[str, float]:
    """
    Compute evaluation metrics for the
    Hugging Face Trainer.
    """

    predictions = np.argmax(
        eval_prediction.predictions,
        axis=1,
    )

    return _calculate_metrics(
        labels=eval_prediction.label_ids,
        predictions=predictions,
    )


# =====================================================
# NUMPY METRICS
# =====================================================

def compute_prediction_metrics(
    predictions: np.ndarray,
    labels: np.ndarray,
) -> dict[str, float]:
    """
    Compute evaluation metrics from
    prediction arrays.

    Used during final model evaluation.
    """

    return _calculate_metrics(
        labels=labels,
        predictions=predictions,
    )


# =====================================================
# CLASSIFICATION REPORT
# =====================================================

def build_classification_report(
    predictions: np.ndarray,
    labels: np.ndarray,
) -> pd.DataFrame:
    """
    Generate a classification report.
    """

    report = classification_report(
        labels,
        predictions,
        labels=LABEL_IDS,
        target_names=TARGET_NAMES,
        output_dict=True,
        zero_division=0,
    )

    return (
        pd.DataFrame(report)
        .transpose()
    )


# =====================================================
# CONFUSION MATRIX
# =====================================================

def build_confusion_matrix(
    predictions: np.ndarray,
    labels: np.ndarray,
) -> pd.DataFrame:
    """
    Generate a confusion matrix.
    """

    matrix = confusion_matrix(
        labels,
        predictions,
        labels=LABEL_IDS,
    )

    return pd.DataFrame(
        matrix,
        index=[
            f"True_{label}"
            for label in TARGET_NAMES
        ],
        columns=[
            f"Pred_{label}"
            for label in TARGET_NAMES
        ],
    )