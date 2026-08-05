"""
=========================================================
RoBERTa Focal Trainer
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect
          Processing (NO CAP)

Description
-----------
Configure the Hugging Face Trainer for supervised
RoBERTa sentiment fine-tuning using weighted
Focal Loss.

Experiment
----------
Experiment 4:
Fine-tuned CardiffNLP RoBERTa + Weighted Focal Loss
"""

from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

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
# FOCAL LOSS
# =====================================================

class FocalLoss(nn.Module):
    """
    Weighted Multi-class Focal Loss.
    """

    def __init__(
        self,
        class_weights: torch.Tensor,
        gamma: float = 2.0,
    ):
        super().__init__()

        self.gamma = gamma
        self.register_buffer(
            "class_weights",
            class_weights,
        )

    def forward(
        self,
        logits: torch.Tensor,
        labels: torch.Tensor,
    ) -> torch.Tensor:

        log_probs = F.log_softmax(
            logits,
            dim=1,
        )

        log_pt = log_probs.gather(
            1,
            labels.unsqueeze(1),
        ).squeeze(1)

        pt = log_pt.exp()

        ce_loss = F.nll_loss(
            log_probs,
            labels,
            weight=self.class_weights,
            reduction="none",
        )

        loss = (
            (1 - pt) ** self.gamma
        ) * ce_loss

        return loss.mean()


# =====================================================
# FOCAL TRAINER
# =====================================================

class FocalTrainer(Trainer):
    """
    Trainer using weighted focal loss.
    """

    def __init__(
        self,
        *args,
        class_weights: torch.Tensor,
        gamma: float = 2.0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.loss_fn = FocalLoss(
            class_weights=class_weights,
            gamma=gamma,
        )

    def compute_loss(
        self,
        model,
        inputs,
        return_outputs=False,
        **kwargs,
    ):
        """
        Compute weighted focal loss.
        """

        labels = inputs.pop(
            "labels",
            None,
        )

        if labels is None:
            labels = inputs.pop(
                "label"
            )

        outputs = model(
            **inputs
        )

        logits = outputs.logits

        if (
            self.loss_fn.class_weights.device
            != logits.device
        ):
            self.loss_fn = (
                self.loss_fn.to(
                    logits.device
                )
            )

        loss = self.loss_fn(
            logits.view(
                -1,
                model.config.num_labels,
            ),
            labels.view(-1),
        )

        if return_outputs:
            return (
                loss,
                outputs,
            )

        return loss

# =====================================================
# TRAINER
# =====================================================

def build_focal_trainer(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    tokenized_dataset,
    data_collator: DataCollatorWithPadding,
    output_dir: Path,
    class_weights: torch.Tensor,
    gamma: float = 2.0,
    compute_metrics=compute_metrics,
    callbacks: list[TrainerCallback] | None = None,
) -> FocalTrainer:
    """
    Build and configure the Hugging Face Trainer
    using weighted focal loss.
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

    trainer = FocalTrainer(

        # -------------------------------------------------
        # Core components
        # -------------------------------------------------

        model=model,
        args=training_args,
        processing_class=tokenizer,
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
        # Focal Loss
        # -------------------------------------------------

        class_weights=class_weights,

        gamma=gamma,

        # -------------------------------------------------
        # Callbacks
        # -------------------------------------------------

        callbacks=callbacks,
    )

    return trainer