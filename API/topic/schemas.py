"""
=========================================================
BERTopic Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Shared data models for BERTopic training,
inference, and analysis.
"""

from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
)

# =====================================================
# TOPIC PREDICTION
# =====================================================


class TopicPrediction(BaseModel):
    """
    Topic prediction for a single document.
    """

    topic_id: int = Field(
        ...,
        description="Predicted BERTopic topic ID.",
    )

    topic_name: str = Field(
        ...,
        description="Human-readable topic name.",
    )

    probability: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Probability of the predicted topic. "
            "None when probabilities are unavailable."
        ),
    )

    keywords: list[str] = Field(
        default_factory=list,
        description="Representative topic keywords.",
    )

    model_version: str = Field(
        ...,
        description="BERTopic model version.",
    )


# =====================================================
# TOPIC INFORMATION
# =====================================================


class TopicInfo(BaseModel):
    """
    Metadata describing a discovered topic.
    """

    topic_id: int = Field(
        ...,
        description="BERTopic topic ID.",
    )

    topic_name: str = Field(
        ...,
        description="Human-readable topic name.",
    )

    document_count: int = Field(
        ...,
        ge=0,
        description="Number of documents assigned to this topic.",
    )

    keywords: list[str] = Field(
        default_factory=list,
        description="Representative topic keywords.",
    )


# =====================================================
# MODEL INFORMATION
# =====================================================


class TopicModelInfo(BaseModel):
    """
    BERTopic model metadata.
    """

    model_version: str = Field(
        ...,
        description="Model version.",
    )

    topic_count: int = Field(
        ...,
        ge=0,
        description="Number of discovered topics (excluding outliers).",
    )

    outlier_topic: int = Field(
        default=-1,
        description="Reserved BERTopic outlier topic ID.",
    )


# =====================================================
# TRAINING SUMMARY
# =====================================================


class TopicTrainingSummary(BaseModel):
    """
    Summary produced after BERTopic training.
    """

    model_version: str

    document_count: int = Field(
        ge=0,
    )

    topic_count: int = Field(
        ge=0,
    )

    outlier_count: int = Field(
        ge=0,
    )

    embedding_model: str

    saved_model_path: str