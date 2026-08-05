"""
=========================================================
RoBERTa Fine-tuning Pipeline (Focal Loss)
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect
          Processing (NO CAP)

Description
-----------
Experiment 4:
Fine-tune the CardiffNLP RoBERTa sentiment model
using weighted focal loss.

Responsibilities
----------------
1. Load DatasetDict
2. Load tokenizer
3. Tokenize dataset
4. Compute class weights
5. Load pretrained model
6. Build focal Trainer
7. Train model
8. Save model
9. Save tokenizer
10. Save trainer state
"""

from pathlib import Path
import logging

import numpy as np
import torch

from datasets import DatasetDict

from sklearn.utils.class_weight import (
    compute_class_weight,
)

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    PreTrainedTokenizerBase,
    Trainer,
)

from .dataset import (
    dataset_pipeline,
    LABEL2ID,
    ID2LABEL,
)

from .trainer_focal import (
    build_focal_trainer,
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


# =====================================================
# MODEL CONFIGURATION
# =====================================================

MODEL_NAME = (
    "cardiffnlp/twitter-roberta-base-sentiment-latest"
)

TOKENIZER_NAME = MODEL_NAME

TEXT_COLUMN = "sentiment_text"

MAX_LENGTH = 512

NUM_LABELS = len(LABEL2ID)


# =====================================================
# TOKENIZATION
# =====================================================

def tokenize_dataset(
    dataset: DatasetDict,
    tokenizer: PreTrainedTokenizerBase,
) -> DatasetDict:
    """
    Tokenize the DatasetDict.
    """

    logging.info(
        "Tokenizing dataset..."
    )

    def tokenize_function(
        examples,
    ):
        return tokenizer(
            examples[TEXT_COLUMN],
            truncation=True,
            max_length=MAX_LENGTH,
        )

    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        desc="Tokenizing",
    )

    columns_to_keep = {
        "input_ids",
        "attention_mask",
        "label",
    }

    columns_to_remove = [
        column
        for column in tokenized_dataset[
            "train"
        ].column_names
        if column not in columns_to_keep
    ]

    tokenized_dataset = (
        tokenized_dataset.remove_columns(
            columns_to_remove
        )
    )

    tokenized_dataset.set_format(
        type="torch",
    )

    logging.info(
        "Tokenization completed."
    )

    return tokenized_dataset


# =====================================================
# LOAD MODEL
# =====================================================

def load_model() -> AutoModelForSequenceClassification:
    """
    Load pretrained RoBERTa model.
    """

    logging.info(
        "Loading pretrained model..."
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            MODEL_NAME,
            num_labels=NUM_LABELS,
            id2label=ID2LABEL,
            label2id=LABEL2ID,
        )
    )

    logging.info(
        "Loaded model: %s",
        MODEL_NAME,
    )

    logging.info(
        "Number of labels: %d",
        model.config.num_labels,
    )

    return model

# =====================================================
# TRAINING PIPELINE
# =====================================================

def training_pipeline(
    experiment_name: str = "experiment_4",
) -> Trainer:
    """
    Complete RoBERTa focal-loss fine-tuning pipeline.
    """

    logging.info("=" * 60)
    logging.info(
        "Starting %s",
        experiment_name,
    )
    logging.info("=" * 60)

    model_dir = (
        BASE_DIR
        / "models"
        / experiment_name
    )

    model_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -------------------------------------------------
    # Dataset
    # -------------------------------------------------

    dataset = dataset_pipeline()

    # -------------------------------------------------
    # Tokenizer
    # -------------------------------------------------

    tokenizer = (
        AutoTokenizer.from_pretrained(
            TOKENIZER_NAME,
        )
    )

    # -------------------------------------------------
    # Compute class weights
    # -------------------------------------------------

    train_labels = np.asarray(
        dataset["train"]["label"]
    )

    tokenized_dataset = tokenize_dataset(
        dataset,
        tokenizer,
    )

    if isinstance(
        train_labels,
        torch.Tensor,
    ):
        train_labels = (
            train_labels.cpu().numpy()
        )

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(train_labels),
        y=train_labels,
    )

    class_weights = torch.tensor(
        class_weights,
        dtype=torch.float32,
    )

    logging.info(
        "Class weights: %s",
        class_weights.tolist(),
    )

    # -------------------------------------------------
    # Model
    # -------------------------------------------------

    model = load_model()

    # -------------------------------------------------
    # Dynamic padding
    # -------------------------------------------------

    data_collator = (
        DataCollatorWithPadding(
            tokenizer=tokenizer,
        )
    )

    # -------------------------------------------------
    # Focal Trainer
    # -------------------------------------------------

    logging.info(
        "Using gamma = %.1f",
        2.0,
    )

    trainer = build_focal_trainer(
        model=model,
        tokenizer=tokenizer,
        tokenized_dataset=tokenized_dataset,
        data_collator=data_collator,
        output_dir=model_dir,
        class_weights=class_weights,
        gamma=2.0,
    )

    # -------------------------------------------------
    # Training
    # -------------------------------------------------

    logging.info(
        "Starting focal-loss training..."
    )

    train_result = trainer.train()

    logging.info(
        "Training completed."
    )

    # -------------------------------------------------
    # Save model
    # -------------------------------------------------

    logging.info(
        "Saving model..."
    )

    trainer.save_model(
        model_dir,
    )

    tokenizer.save_pretrained(
        model_dir,
    )

    trainer.save_metrics(
        "train",
        train_result.metrics,
    )

    trainer.save_state()

    logging.info(
        "Model saved to:"
    )

    logging.info(
        "%s",
        model_dir,
    )

    return trainer


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Entry point.
    """

    training_pipeline(
        experiment_name="experiment_4",
    )


if __name__ == "__main__":
    main()