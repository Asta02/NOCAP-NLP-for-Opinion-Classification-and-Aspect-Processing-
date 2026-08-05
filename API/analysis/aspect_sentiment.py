"""
=========================================================
Aspect Sentiment Analyzer
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Aspect-level sentiment analysis.

Pipeline

Review
    ↓
AspectExtractor
    ↓
ExtractedAspect
    ↓
SentimentInference
    ↓
AspectResult
"""

from __future__ import annotations

from sentiment.inference import (
    get_sentiment_inference,
)

from .aspect_extractor import (
    AspectExtractor,
)

from .schemas import (
    AspectResult,
    ExtractedAspect,
)


class AspectSentimentAnalyzer:
    """
    Predict sentiment for extracted aspects.
    """

    def __init__(self) -> None:

        self.extractor = AspectExtractor()

        self.sentiment = (
            get_sentiment_inference()
        )

    def analyze(
        self,
        review: str,
    ) -> list[AspectResult]:
        """
        Analyze aspect sentiment from a review.
        """

        extracted = (
            self.extractor.extract(
                review
            )
        )

        return self.analyze_extracted(
            extracted
        )

    def analyze_extracted(
        self,
        aspects: list[
            ExtractedAspect
        ],
    ) -> list[AspectResult]:
        """
        Predict sentiment for extracted aspects.
        """

        results: list[
            AspectResult
        ] = []

        for aspect in aspects:

            prediction = (
                self.sentiment.predict(
                    aspect.phrase
                )
            )

            results.append(
                AspectResult(
                    aspect=aspect.aspect,
                    phrase=aspect.phrase,
                    prediction=prediction,
                )
            )

        return results

# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Interactive CLI.
    """

    analyzer = (
        AspectSentimentAnalyzer()
    )

    print("=" * 60)
    print("Aspect Sentiment Analyzer")
    print("=" * 60)
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:

        review = input(
            "\nEnter review:\n> "
        ).strip()

        if review.lower() in {
            "exit",
            "quit",
            "q",
        }:
            print("\nGoodbye!")
            break

        try:

            results = (
                analyzer.analyze(
                    review
                )
            )

            print()

            if not results:

                print(
                    "No aspects detected."
                )

                continue

            print("=" * 60)
            print("Aspect Sentiment Results")
            print("=" * 60)

            for result in results:

                print(
                    result.model_dump_json(
                        indent=4,
                    )
                )

            print("=" * 60)

        except KeyboardInterrupt:

            print("\n\nGoodbye!")
            break

        except Exception as error:

            print(
                f"\nError: {error}"
            )


if __name__ == "__main__":
    main()