"""
=========================================================
Review Analyzer
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
High-level review analysis service.

Pipeline
--------

Review
    │
    ├────────────► SentimentInference
    │
    ├────────────► AspectSentimentAnalyzer
    │
    └────────────► TopicInference
                    │
                    ▼
             ReviewAnalysis
"""

from __future__ import annotations

from time import perf_counter
from typing import Sequence

from sentiment.inference import (
    get_sentiment_inference,
)

from topic.inference import (
    get_topic_inference,
)

from .aspect_sentiment import (
    AspectSentimentAnalyzer,
)

from .profiler import (
    AnalysisProfile,
)

from .schemas import (
    ReviewAnalysis,
)


class ReviewAnalyzer:
    """
    High-level review analysis service.

    This class orchestrates all NLP components
    and returns a unified ReviewAnalysis object.
    """

    def __init__(self) -> None:

        self.sentiment = (
            get_sentiment_inference()
        )

        self.aspect_sentiment = (
            AspectSentimentAnalyzer()
        )

        self.topic = (
            get_topic_inference()
        )

        self.last_profile = (
            AnalysisProfile()
        )

    def analyze(
        self,
        text: str,
    ) -> ReviewAnalysis:
        """
        Analyze a single review.
        """

        review = text.strip()

        if not review:

            raise ValueError(
                "Input review cannot be empty."
            )

        profile = AnalysisProfile()

        start = perf_counter()

        t0 = perf_counter()

        sentiment = (
            self.sentiment.predict(
                review
            )
        )

        t1 = perf_counter()

        profile.sentiment_ms = (
            t1 - t0
        ) * 1000

        aspects = (
            self.aspect_sentiment.analyze(
                review
            )
        )

        t2 = perf_counter()

        profile.aspect_ms = (
            t2 - t1
        ) * 1000

        topic = (
            self.topic.predict(
                review
            )
        )

        t3 = perf_counter()

        profile.topic_ms = (
            t3 - t2
        ) * 1000

        profile.total_ms = (
            t3 - start
        ) * 1000

        self.last_profile = (
            profile
        )

        return ReviewAnalysis(
            text=review,
            sentiment=sentiment,
            aspects=aspects,
            topic=topic,
            processing_time_ms=profile.total_ms,
        )

    def analyze_batch(
        self,
        texts: Sequence[str],
    ) -> list[ReviewAnalysis]:
        """
        Analyze multiple reviews.
        """

        reviews = [

            review.strip()

            for review in texts

            if review.strip()

        ]

        if not reviews:

            raise ValueError(
                "Input list cannot be empty."
            )

        return [

            self.analyze(review)

            for review in reviews

        ]

    def health(
        self,
    ) -> dict[str, object]:
        """
        Return analyzer health information.
        """

        sentiment = (
            self.sentiment.health()
        )

        topic = (
            self.topic.health()
        )

        return {

            "status": "ready",

            "model": sentiment["model"],

            "device": sentiment["device"],

            "topic_model": (
                topic.model_version
            ),

            "components": {

                "sentiment": True,

                "aspect_extractor": True,

                "aspect_sentiment": True,

                "topic": True,

            },

        }


def main() -> None:
    """
    Interactive Review Analyzer CLI.
    """

    analyzer = ReviewAnalyzer()

    health = analyzer.health()

    print("=" * 60)
    print("Review Analyzer")
    print("=" * 60)

    print(
        f"Model       : {health['model']}"
    )

    print(
        f"Device      : {health['device']}"
    )

    print(
        f"Topic Model : "
        f"{health['topic_model']}"
    )

    print("=" * 60)
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:

        try:

            review = input(
                "\nEnter review:\n> "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt,
        ):

            print("\n\nGoodbye!")

            break

        if review.lower() in {
            "exit",
            "quit",
            "q",
        }:

            print("\nGoodbye!")

            break

        try:

            analysis = (
                analyzer.analyze(
                    review
                )
            )

            profile = (
                analyzer.last_profile
            )

            print()

            print("=" * 60)
            print("Analysis Summary")
            print("=" * 60)

            print(
                f"Overall Sentiment : "
                f"{analysis.sentiment.label}"
            )

            print(
                f"Confidence        : "
                f"{analysis.sentiment.confidence:.4f}"
            )

            print(
                f"Topic             : "
                f"{analysis.topic.topic_name}"
            )

            print(
                f"Topic ID          : "
                f"{analysis.topic.topic_id}"
            )

            print(
                "Keywords          : "
                + ", ".join(
                    analysis.topic.keywords
                )
            )

            print(
                f"Aspects Detected  : "
                f"{len(analysis.aspects)}"
            )

            print(
                f"Processing Time   : "
                f"{analysis.processing_time_ms:.2f} ms"
            )

            print()

            print("Pipeline Profiling")
            print("-" * 60)

            print(
                f"Sentiment         : "
                f"{profile.sentiment_ms:.2f} ms"
            )

            print(
                f"Aspect            : "
                f"{profile.aspect_ms:.2f} ms"
            )

            print(
                f"Topic             : "
                f"{profile.topic_ms:.2f} ms"
            )

            print(
                f"Slowest Component : "
                f"{profile.slowest_component}"
            )

            if analysis.aspects:

                print()

                print("Aspect Sentiment")
                print("-" * 60)

                for aspect in analysis.aspects:

                    print(
                        f"{aspect.aspect:<20}"
                        f"{aspect.prediction.label:<10}"
                        f"{aspect.prediction.confidence:.4f}"
                    )

            print()

            print("JSON Output")
            print("-" * 60)

            print(
                analysis.model_dump_json(
                    indent=4,
                )
            )

            print("=" * 60)

        except Exception as error:

            print(
                f"\nError: {error}"
            )


if __name__ == "__main__":
    main()