"""
=========================================================
Repository Test
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Simple repository test.
"""

from __future__ import annotations

from analysis.schemas import (
    AspectResult,
    ReviewAnalysis,
)

from database.repository import (
    ReviewRepository,
)

from sentiment.schemas import (
    SentimentPrediction,
)

from topic.schemas import (
    TopicPrediction,
)


def build_prediction(
    label: str,
    label_id: int,
) -> SentimentPrediction:

    return SentimentPrediction(
        label=label,
        label_id=label_id,
        confidence=0.99,
        probabilities={
            "Negative": 0.01,
            "Neutral": 0.00,
            "Positive": 0.99,
        },
        model_version="experiment_3",
    )


def main() -> None:

    repository = ReviewRepository()

    analysis = ReviewAnalysis(

        text=(
            "The salary is great "
            "but management is poor."
        ),

        sentiment=build_prediction(
            "Negative",
            0,
        ),

        aspects=[

            AspectResult(

                aspect="Salary",

                phrase="salary is great",

                prediction=build_prediction(
                    "Positive",
                    2,
                ),

            ),

            AspectResult(

                aspect="Management",

                phrase="management is poor",

                prediction=build_prediction(
                    "Negative",
                    0,
                ),

            ),

        ],

        topic=TopicPrediction(

            topic_id=3,

            topic_name="Management",

            probability=0.91,

            keywords=[
                "management",
                "leader",
                "promotion",
            ],

            model_version="bertopic_v1",

        ),

        processing_time_ms=100.0,

    )

    review = repository.save(
        analysis
    )

    print("=" * 60)
    print("Repository Test")
    print("=" * 60)

    print(
        f"Saved Review ID : {review.id}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()