"""
=========================================================
RoBERTa Trainer
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing (NO CAP)

Description
-----------
Configure the Hugging Face Trainer for supervised
RoBERTa sentiment fine-tuning.

Responsibilities
----------------
1. Compute evaluation metrics
2. Build TrainingArguments
3. Build Trainer
"""

from pathlib import Path

import numpy as np
import torch

from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    precision_recall_fscore_support,
)

from transformers import (
    TrainingArguments,
)

from transformers.trainer_utils import (
    EvalPrediction,
)

from .metrics import compute_metrics


# =====================================================
# TRAINING CONSTANTS
# =====================================================

NUM_EPOCHS = 3

LEARNING_RATE = 2e-5

TRAIN_BATCH_SIZE = 16

EVAL_BATCH_SIZE = 16

WEIGHT_DECAY = 0.01

WARMUP_RATIO = 0.10

LOGGING_STEPS = 100

EARLY_STOPPING_PATIENCE = 2

SEED = 42

# =====================================================
# TRAINING ARGUMENTS
# =====================================================

def build_training_arguments(
    output_dir: Path,
) -> TrainingArguments:
    """
    Create Hugging Face TrainingArguments.
    """

    use_bf16 = (
        torch.cuda.is_available()
        and torch.cuda.is_bf16_supported()
    )

    use_fp16 = (
        torch.cuda.is_available()
        and not use_bf16
    )

    return TrainingArguments(

        # -------------------------------------------------
        # Output
        # -------------------------------------------------

        output_dir=str(output_dir),

        # -------------------------------------------------
        # Optimization
        # -------------------------------------------------

        learning_rate=LEARNING_RATE,

        num_train_epochs=NUM_EPOCHS,

        per_device_train_batch_size=TRAIN_BATCH_SIZE,

        per_device_eval_batch_size=EVAL_BATCH_SIZE,

        weight_decay=WEIGHT_DECAY,

        warmup_ratio=WARMUP_RATIO,

        # -------------------------------------------------
        # Evaluation
        # -------------------------------------------------

        eval_strategy="epoch",

        save_strategy="epoch",

        load_best_model_at_end=True,

        metric_for_best_model="f1_macro",

        greater_is_better=True,

        # -------------------------------------------------
        # Logging
        # -------------------------------------------------

        logging_strategy="steps",

        logging_steps=LOGGING_STEPS,

        logging_dir=str(
            output_dir / "logs"
        ),

        # -------------------------------------------------
        # Checkpoints
        # -------------------------------------------------

        save_total_limit=1,

        save_safetensors=True,

        # -------------------------------------------------
        # Dataset
        # -------------------------------------------------

        remove_unused_columns=True,

        # -------------------------------------------------
        # Mixed Precision
        # -------------------------------------------------

        fp16=use_fp16,

        bf16=use_bf16,

        # -------------------------------------------------
        # Reproducibility
        # -------------------------------------------------

        seed=SEED,

        # -------------------------------------------------
        # Reporting
        # -------------------------------------------------

        report_to="none",
    )

from transformers import (
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    Trainer,
    TrainerCallback,
)


# =====================================================
# TRAINER
# =====================================================

def build_trainer(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    tokenized_dataset,
    data_collator: DataCollatorWithPadding,
    output_dir: Path,
    compute_metrics=compute_metrics,
    callbacks: list[TrainerCallback] | None = None,
) -> Trainer:
    """
    Build and configure the Hugging Face Trainer.
    """

    training_args = build_training_arguments(
        output_dir
    )

    if callbacks is None:
        callbacks = [
            EarlyStoppingCallback(
                early_stopping_patience=(
                    EARLY_STOPPING_PATIENCE
                )
            )
        ]

    trainer = Trainer(

        # -------------------------------------------------
        # Core components
        # -------------------------------------------------

        model=model,

        args=training_args,

        tokenizer=tokenizer,

        data_collator=data_collator,

        # -------------------------------------------------
        # Dataset
        # -------------------------------------------------

        train_dataset=tokenized_dataset[
            "train"
        ],

        eval_dataset=tokenized_dataset[
            "validation"
        ],

        # -------------------------------------------------
        # Evaluation
        # -------------------------------------------------

        compute_metrics=compute_metrics,

        # -------------------------------------------------
        # Callbacks
        # -------------------------------------------------

        callbacks=callbacks,
    )

    return trainer