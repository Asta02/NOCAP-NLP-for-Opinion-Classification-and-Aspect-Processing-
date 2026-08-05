"""
=========================================================
RoBERTa Weighted Trainer
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing (NO CAP)

Description
-----------
Configure the Hugging Face Trainer for supervised
RoBERTa sentiment fine-tuning using weighted
cross-entropy loss.

Experiment
----------
Experiment 3:
Fine-tuned CardiffNLP RoBERTa + Weighted Loss
"""

from pathlib import Path

import torch

from transformers import (
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    Trainer,
    TrainerCallback,
)

from .metrics import compute_metrics

from .trainer import (
    build_training_arguments,
    EARLY_STOPPING_PATIENCE,
)


# =====================================================
# WEIGHTED TRAINER
# =====================================================

class WeightedTrainer(Trainer):
    """
    Trainer using weighted cross-entropy loss.
    """

    def __init__(
        self,
        *args,
        class_weights: torch.Tensor,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.loss_fn = torch.nn.CrossEntropyLoss(
            weight=class_weights
        )

    def compute_loss(
        self,
        model,
        inputs,
        return_outputs=False,
        num_items_in_batch=None,
    ):
        """
        Compute weighted cross-entropy loss.
        """

        # Support both "label" and "labels"
        labels = inputs.pop("labels", None)

        if labels is None:
            labels = inputs.pop("label")

        outputs = model(**inputs)

        logits = outputs.logits

        # Ensure the loss function is on the same device as the model
        self.loss_fn = self.loss_fn.to(logits.device)

        loss = self.loss_fn(
            logits.view(-1, model.config.num_labels),
            labels.view(-1),
        )

        if return_outputs:
            return loss, outputs

        return loss

# =====================================================
# TRAINER
# =====================================================

def build_weighted_trainer(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    tokenized_dataset,
    data_collator: DataCollatorWithPadding,
    output_dir: Path,
    class_weights: torch.Tensor,
    compute_metrics=compute_metrics,
    callbacks: list[TrainerCallback] | None = None,
) -> WeightedTrainer:
    """
    Build and configure the weighted Hugging Face Trainer.
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

    trainer = WeightedTrainer(

        # -------------------------------------------------
        # Core components
        # -------------------------------------------------

        model=model,
        args=training_args,
        processing_class=tokenizer,
        data_collator=data_collator

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
        # Weighted Loss
        # -------------------------------------------------

        class_weights=class_weights,

        # -------------------------------------------------
        # Callbacks
        # -------------------------------------------------

        callbacks=callbacks,
    )

    return trainer