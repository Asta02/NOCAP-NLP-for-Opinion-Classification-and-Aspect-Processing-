"""
=========================================================
RoBERTa Model Evaluation
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing (NO CAP)

Description
-----------
Evaluate a fine-tuned RoBERTa sentiment classifier on the
held-out test dataset.

Outputs
-------
summary.csv
classification_report.csv
confusion_matrix.csv
predictions.csv
metrics.json
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Mapping, cast

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from datasets import Dataset

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)
from transformers.modeling_utils import PreTrainedModel
from transformers.data.data_collator import DataCollatorWithPadding
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.trainer import Trainer
from transformers.trainer_utils import PredictionOutput

from .dataset import (
    TEXT_COLUMN,
    ENCODED_LABEL_COLUMN,
)

from .metrics import (
    LABEL_IDS,
    TARGET_NAMES,
    build_classification_report,
    build_confusion_matrix,
    compute_prediction_metrics,
)

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = (
    BASE_DIR
    / "data"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
)

EVALUATION_DIR = (
    DATA_DIR
    / "evaluation"
)

SPLIT_DIR = (
    DATA_DIR
    / "processed"
    / "splits"
)

TEST_FILE = (
    SPLIT_DIR
    / "test.csv"
)

# =====================================================
# CONFIGURATION
# =====================================================

MAX_LENGTH = 512

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# =====================================================
# HELPERS
# =====================================================


def extract_logits(
    prediction_output: PredictionOutput,
) -> np.ndarray:
    """
    Extract logits from PredictionOutput.
    """

    logits = prediction_output.predictions

    if isinstance(logits, tuple):
        logits = logits[0]

    return cast(np.ndarray, logits)


def extract_labels(
    prediction_output: PredictionOutput,
) -> np.ndarray:
    """
    Extract labels from PredictionOutput.
    """

    labels = prediction_output.label_ids

    if labels is None:
        raise ValueError(
            "PredictionOutput.label_ids is None."
        )

    if isinstance(labels, tuple):
        labels = labels[0]

    return cast(np.ndarray, labels)


# =====================================================
# MODEL
# =====================================================


def load_model(
    experiment_name: str,
) -> PreTrainedModel:
    """
    Load a trained sentiment model.
    """

    model_path = (
        MODEL_DIR
        / experiment_name
    )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found:\n{model_path}"
        )

    logger.info(
        "Loading model from %s",
        model_path,
    )

    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    assert isinstance(model, PreTrainedModel)

    model.to(DEVICE) # pyright: ignore[reportArgumentType]
    model.eval()

    return model


# =====================================================
# TOKENIZER
# =====================================================


def load_tokenizer(
    experiment_name: str,
) -> PreTrainedTokenizerBase:
    """
    Load tokenizer associated with the trained model.
    """

    model_path = (
        MODEL_DIR
        / experiment_name
    )

    logger.info(
        "Loading tokenizer..."
    )

    return cast(
        PreTrainedTokenizerBase,
        AutoTokenizer.from_pretrained(
            model_path
        ),
    )


# =====================================================
# TEST DATASET
# =====================================================


def load_test_dataset() -> Dataset:
    """
    Load the held-out test dataset.
    """

    logger.info(
        "Loading test dataset..."
    )

    if not TEST_FILE.exists():
        raise FileNotFoundError(
            f"Test dataset not found:\n{TEST_FILE}"
        )

    dataframe = pd.read_csv(
        TEST_FILE
    )

    required_columns = {
        TEXT_COLUMN,
        ENCODED_LABEL_COLUMN,
    }

    missing = (
        required_columns
        .difference(dataframe.columns)
    )

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    logger.info(
        "Loaded %d test samples.",
        len(dataframe),
    )

    return cast(
        Dataset,
        Dataset.from_pandas(
            dataframe,
            preserve_index=False,
        ),
    )


# =====================================================
# TOKENIZATION
# =====================================================


def tokenize_dataset(
    dataset: Dataset,
    tokenizer: PreTrainedTokenizerBase,
) -> tuple[
    Dataset,
    DataCollatorWithPadding,
]:
    """
    Tokenize the test dataset.
    """

    logger.info(
        "Tokenizing test dataset..."
    )

    def tokenize(
        batch: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        return tokenizer(
            batch[TEXT_COLUMN],
            truncation=True,
            max_length=MAX_LENGTH,
        )

    tokenized_dataset = cast(
        Dataset,
        dataset.map(
            tokenize,
            batched=True,
            desc="Tokenizing",
        ),
    )

    keep_columns = {
        "input_ids",
        "attention_mask",
        ENCODED_LABEL_COLUMN,
    }

    remove_columns = [
        column
        for column in tokenized_dataset.column_names
        if column not in keep_columns
    ]

    tokenized_dataset.set_format(
        type="torch",
    )

    tokenized_dataset = cast(
        Dataset,
        tokenized_dataset.remove_columns(
            remove_columns
        ),
    )

    data_collator = DataCollatorWithPadding(
        tokenizer=tokenizer,
    )

    return (
        tokenized_dataset,
        data_collator,
    )


# =====================================================
# PREDICTION
# =====================================================


def predict(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    tokenized_dataset: Dataset,
    data_collator: DataCollatorWithPadding,
) -> PredictionOutput:
    """
    Run inference on the test dataset.
    """

    logger.info(
        "Running predictions..."
    )

    trainer: Trainer = Trainer(
        model=model,
        processing_class=tokenizer,
        data_collator=data_collator,
    )

    prediction_output = cast(
        PredictionOutput,
        trainer.predict(cast(Any, tokenized_dataset))
    )

    logger.info(
        "Prediction completed."
    )

    return prediction_output


# =====================================================
# PREDICTIONS DATAFRAME
# =====================================================


def build_predictions_dataframe(
    original_dataset: Dataset,
    prediction_output: PredictionOutput,
) -> pd.DataFrame:
    """
    Build a prediction table for
    error analysis.
    """

    dataframe = cast(
        pd.DataFrame,
        original_dataset.to_pandas(),
    ).copy()

    logits = extract_logits(
        prediction_output
    )

    labels = extract_labels(
        prediction_output
    )

    predictions = logits.argmax(
        axis=1
    )

    probabilities = F.softmax(
        torch.from_numpy(logits),
        dim=1,
    )

    confidence = (
        probabilities
        .max(dim=1)
        .values
        .cpu()
        .numpy()
    )

    dataframe["true_label"] = labels

    dataframe["predicted_label"] = predictions

    dataframe["true_sentiment"] = (
        dataframe["true_label"]
        .map(
            dict(
                zip(
                    LABEL_IDS,
                    TARGET_NAMES,
                )
            )
        )
    )

    dataframe["predicted_sentiment"] = (
        dataframe["predicted_label"]
        .map(
            dict(
                zip(
                    LABEL_IDS,
                    TARGET_NAMES,
                )
            )
        )
    )

    dataframe["confidence"] = confidence

    logger.info(
        "Prediction dataframe created."
    )

    return dataframe


# =====================================================
# EVALUATION
# =====================================================


def evaluate_predictions(
    prediction_output: PredictionOutput,
) -> tuple[
    dict[str, float],
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Compute evaluation metrics and reports.
    """

    logits = extract_logits(
        prediction_output
    )

    labels = extract_labels(
        prediction_output
    )

    predictions = logits.argmax(
        axis=1
    )

    metrics = (
        compute_prediction_metrics(
            predictions,
            labels,
        )
    )

    report_df = (
        build_classification_report(
            predictions,
            labels,
        )
    )

    confusion_df = (
        build_confusion_matrix(
            predictions,
            labels,
        )
    )

    logger.info(
        "Evaluation metrics generated."
    )

    return (
        metrics,
        report_df,
        confusion_df,
    )


# =====================================================
# SAVE RESULTS
# =====================================================


def save_results(
    experiment_name: str,
    metrics: dict[str, float],
    report_df: pd.DataFrame,
    confusion_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
) -> None:
    """
    Save evaluation outputs.
    """

    output_dir = (
        EVALUATION_DIR
        / experiment_name
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Saving evaluation results..."
    )

    # ---------------------------------------------
    # summary.csv
    # ---------------------------------------------

    summary_df = pd.DataFrame(
        {
            "Metric": [
                "Accuracy",
                "Macro Precision",
                "Macro Recall",
                "Macro F1",
                "Weighted F1",
                "Cohen Kappa",
            ],
            "Value": [
                metrics["accuracy"],
                metrics["precision_macro"],
                metrics["recall_macro"],
                metrics["f1_macro"],
                metrics["f1_weighted"],
                metrics["kappa"],
            ],
        }
    )

    summary_df.to_csv(
        output_dir / "summary.csv",
        index=False,
    )

    # ---------------------------------------------
    # metrics.json
    # ---------------------------------------------

    with open(
        output_dir / "metrics.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4,
        )

    # ---------------------------------------------
    # classification_report.csv
    # ---------------------------------------------

    report_df.to_csv(
        output_dir / "classification_report.csv"
    )

    # ---------------------------------------------
    # confusion_matrix.csv
    # ---------------------------------------------

    confusion_df.to_csv(
        output_dir / "confusion_matrix.csv"
    )

    # ---------------------------------------------
    # predictions.csv
    # ---------------------------------------------

    predictions_df.to_csv(
        output_dir / "predictions.csv",
        index=False,
    )

    logger.info(
        "Results saved to %s",
        output_dir,
    )


# =====================================================
# PIPELINE
# =====================================================

def evaluation_pipeline(
    experiment_name: str = "experiment_2",
) -> None:
    """
    Evaluate a trained sentiment model on the
    held-out test dataset.
    """

    logger.info("=" * 60)
    logger.info(
        "Evaluating %s",
        experiment_name,
    )
    logger.info("=" * 60)

    # ---------------------------------------------
    # Load model and tokenizer
    # ---------------------------------------------

    model = load_model(
        experiment_name
    )

    tokenizer = load_tokenizer(
        experiment_name
    )

    # ---------------------------------------------
    # Load dataset
    # ---------------------------------------------

    original_dataset = (
        load_test_dataset()
    )

    tokenized_dataset, data_collator = (
        tokenize_dataset(
            original_dataset,
            tokenizer,
        )
    )

    # ---------------------------------------------
    # Prediction
    # ---------------------------------------------

    prediction_output = predict(
        model=model,
        tokenizer=tokenizer,
        tokenized_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # ---------------------------------------------
    # Evaluation
    # ---------------------------------------------

    metrics, report_df, confusion_df = (
        evaluate_predictions(
            prediction_output
        )
    )

    predictions_df = (
        build_predictions_dataframe(
            original_dataset,
            prediction_output,
        )
    )

    # ---------------------------------------------
    # Save outputs
    # ---------------------------------------------

    save_results(
        experiment_name=experiment_name,
        metrics=metrics,
        report_df=report_df,
        confusion_df=confusion_df,
        predictions_df=predictions_df,
    )

    # ---------------------------------------------
    # Console summary
    # ---------------------------------------------

    logger.info("=" * 60)
    logger.info("Evaluation Summary")
    logger.info("=" * 60)

    for metric_name, value in metrics.items():

        logger.info(
            "%-18s : %.4f",
            metric_name.replace(
                "_",
                " "
            ).title(),
            value,
        )

    logger.info("=" * 60)
    logger.info(
        "Evaluation completed."
    )


# =====================================================
# EXPERIMENT DISCOVERY
# =====================================================

def discover_experiments() -> list[str]:
    """
    Discover trained experiment models.
    """

    if not MODEL_DIR.exists():
        return []

    experiments = []

    for path in MODEL_DIR.iterdir():

        if (
            path.is_dir()
            and path.name.startswith("experiment_")
            and (path / "config.json").exists()
        ):
            experiments.append(path.name)

    return sorted(experiments)
    
# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Evaluate every discovered experiment.
    """

    experiments = discover_experiments()

    logger.info(
        "Discovered %d experiment(s).",
        len(experiments),
    )

    for experiment in experiments:

        logger.info("")

        try:
            evaluation_pipeline(
                experiment_name=experiment,
            )

        except Exception:
            logger.exception(
                "Skipping %s",
                experiment,
            )

    logger.info(
        "Finished evaluating all experiments."
    )

if __name__ == "__main__":
    main()