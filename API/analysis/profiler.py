"""
=========================================================
Analysis Profiler
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Simple profiling utilities for measuring
the execution time of each NLP component.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AnalysisProfile:
    """
    Execution time of each pipeline stage.
    """

    sentiment_ms: float = 0.0

    aspect_ms: float = 0.0

    topic_ms: float = 0.0

    total_ms: float = 0.0

    @property
    def slowest_component(self) -> str:

        values = {
            "sentiment": self.sentiment_ms,
            "aspect": self.aspect_ms,
            "topic": self.topic_ms,
        }

        return max(
            values,
            key=values.get,
        )