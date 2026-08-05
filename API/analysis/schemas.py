"""
=========================================================
Analysis Schemas
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Shared data models for the analysis pipeline.
"""

from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
)

from sentiment.schemas import (
    SentimentPrediction,
)

from topic.schemas import (
    TopicPrediction,
)

# =====================================================
# EXTRACTED ASPECT
# =====================================================


class ExtractedAspect(BaseModel):
    """
    Aspect detected before sentiment analysis.
    """

    aspect: str = Field(
        ...,
        description="Detected aspect.",
    )

    phrase: str = Field(
        ...,
        description="Local phrase describing the aspect.",
    )


# =====================================================
# ASPECT RESULT
# =====================================================


class AspectResult(BaseModel):
    """
    Aspect-level sentiment result.
    """
    aspect: str
    phrase: str
    prediction: SentimentPrediction


# =====================================================
# KEYWORD
# =====================================================


class KeywordResult(BaseModel):
    """
    Keyword extraction result.
    """

    keyword: str

    score: float = Field(
        ge=0.0,
    )


# =====================================================
# SUMMARY
# =====================================================


class SummaryResult(BaseModel):
    """
    Generated review summary.
    """

    text: str


# =====================================================
# RECOMMENDATION
# =====================================================


class RecommendationResult(BaseModel):
    """
    Generated recommendation.
    """

    text: str


# =====================================================
# REVIEW ANALYSIS
# =====================================================


class ReviewAnalysis(BaseModel):
    """
    Complete review analysis.
    """

    text: str

    sentiment: SentimentPrediction

    aspects: list[AspectResult] = Field(
        default_factory=list,
    )

    topic: TopicPrediction | None = None

    keywords: list[KeywordResult] = Field(
        default_factory=list,
    )

    summary: SummaryResult | None = None

    recommendation: RecommendationResult | None = None

    processing_time_ms: float = Field(
        ge=0.0,
    )