"""
=========================================================
BERTopic Inference
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Production BERTopic inference service.

Responsibilities
----------------
1. Load trained BERTopic model
2. Predict document topics
3. Predict batch topics
4. Provide cached topic metadata

This module MUST NOT

- train BERTopic
- evaluate topics
- visualize topics
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Sequence

from bertopic import BERTopic

from .constants import (
    DEFAULT_MODEL_PATH,
    MODEL_CONFIG,
    OUTLIER_TOPIC_ID,
    TOPIC_CONFIG,
)

from .schemas import (
    TopicInfo,
    TopicModelInfo,
    TopicPrediction,
)

# =====================================================
# TOPIC INFERENCE
# =====================================================


class TopicInference:
    """
    Production BERTopic inference service.

    The model is loaded once during initialization
    and reused for all predictions.
    """

    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
    ) -> None:

        model_path = Path(model_path)

        if not model_path.exists():

            raise FileNotFoundError(
                f"BERTopic model not found:\n"
                f"{model_path}"
            )

        self.model_path = model_path

        self.model = BERTopic.load(
            model_path,
        )

        self.topic_info = (
            self.model.get_topic_info()
        )

        # ---------------------------------------------
        # Cache initialization
        # ---------------------------------------------

        self.topic_lookup = (
            self._build_topic_lookup()
        )

        self.keyword_lookup = (
            self._build_keyword_lookup()
        )

        self.topic_cache = (
            self._build_topic_cache()
        )

    # =================================================
    # PROPERTIES
    # =================================================

    @property
    def version(
        self,
    ) -> str:
        """
        Model version.
        """

        return MODEL_CONFIG[
            "version"
        ]

    # =================================================
    # CACHE BUILDERS
    # =================================================

    def _build_topic_lookup(
        self,
    ) -> dict[int, str]:
        """
        Cache topic names.
        """

        lookup: dict[
            int,
            str,
        ] = {}

        for _, row in (
            self.topic_info.iterrows()
        ):

            lookup[
                int(row.Topic)
            ] = str(
                row.Name
            )

        return lookup

    def _build_keyword_lookup(
        self,
    ) -> dict[
        int,
        list[str],
    ]:
        """
        Cache representative keywords.
        """

        lookup: dict[
            int,
            list[str],
        ] = {}

        for topic_id in (
            self.topic_lookup.keys()
        ):

            topic = (
                self.model.get_topic(
                    topic_id
                )
            )

            if topic is None:

                lookup[
                    topic_id
                ] = []

                continue

            lookup[
                topic_id
            ] = [

                word

                for word, _ in topic[
                    : TOPIC_CONFIG["top_n_words"]
                ]
            ]

        return lookup

    def _build_topic_cache(
        self,
    ) -> dict[int, TopicInfo]:
        """
        Cache TopicInfo objects.

        This cache is built AFTER
        topic_lookup and keyword_lookup,
        avoiding recursive dependencies.
        """

        cache: dict[
            int,
            TopicInfo,
        ] = {}

        for _, row in (
            self.topic_info.iterrows()
        ):

            topic_id = int(
                row.Topic
            )

            cache[
                topic_id
            ] = TopicInfo(
                topic_id=topic_id,
                topic_name=self.topic_lookup.get(
                    topic_id,
                    f"Topic {topic_id}",
                ),
                document_count=int(
                    row.Count
                ),
                keywords=self.keyword_lookup.get(
                    topic_id,
                    [],
                ),
            )

        return cache

    # =================================================
    # PRIVATE HELPERS
    # =================================================

    def _topic_name(
        self,
        topic_id: int,
    ) -> str:
        """
        Return cached topic name.
        """

        if (
            topic_id
            == OUTLIER_TOPIC_ID
        ):

            return "Outlier"

        return self.topic_lookup.get(
            topic_id,
            f"Topic {topic_id}",
        )

    def _topic_keywords(
        self,
        topic_id: int,
    ) -> list[str]:
        """
        Return cached keywords.
        """

        return self.keyword_lookup.get(
            topic_id,
            [],
        )

    def _build_prediction(
        self,
        topic_id: int,
        probability: float | None,
    ) -> TopicPrediction:
        """
        Build TopicPrediction.
        """

        return TopicPrediction(
            topic_id=topic_id,
            topic_name=self._topic_name(
                topic_id,
            ),
            probability=probability,
            keywords=self._topic_keywords(
                topic_id,
            ),
            model_version=self.version,
        )

    # =================================================
    # HEALTH
    # =================================================

    def health(
        self,
    ) -> TopicModelInfo:
        """
        Return model metadata.
        """

        topic_count = sum(

            1

            for topic_id in self.topic_cache

            if topic_id != OUTLIER_TOPIC_ID

        )

        return TopicModelInfo(
            model_version=self.version,
            topic_count=topic_count,
            outlier_topic=OUTLIER_TOPIC_ID,
        )

    # =================================================
    # PUBLIC API
    # =================================================

    def predict(
        self,
        text: str,
    ) -> TopicPrediction:
        """
        Predict the topic for one review.
        """

        review = text.strip()

        if not review:

            raise ValueError(
                "Input review cannot be empty."
            )

        topics, probabilities = (
            self.model.transform(
                [review]
            )
        )

        topic_id = int(
            topics[0]
        )

        probability: float | None = None

        if probabilities is not None:

            try:

                # Probability matrix
                probability = float(
                    probabilities[0][
                        topic_id
                    ]
                )

            except (
                IndexError,
                TypeError,
                ValueError,
            ):

                try:

                    # Older BERTopic versions
                    probability = float(
                        probabilities[0]
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    probability = None

        return self._build_prediction(
            topic_id=topic_id,
            probability=probability,
        )

    def predict_batch(
        self,
        texts: Sequence[str],
    ) -> list[TopicPrediction]:
        """
        Predict topics for multiple reviews.
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

        topics, probabilities = (
            self.model.transform(
                reviews
            )
        )

        predictions: list[
            TopicPrediction
        ] = []

        for index, topic_id in enumerate(
            topics
        ):

            probability: float | None = None

            if probabilities is not None:

                try:

                    probability = float(
                        probabilities[
                            index
                        ][
                            topic_id
                        ]
                    )

                except (
                    IndexError,
                    TypeError,
                    ValueError,
                ):

                    try:

                        probability = float(
                            probabilities[
                                index
                            ]
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        probability = None

            predictions.append(
                self._build_prediction(
                    topic_id=int(
                        topic_id
                    ),
                    probability=probability,
                )
            )

        return predictions

    # =================================================
    # TOPIC METADATA
    # =================================================

    def list_topics(
        self,
    ) -> list[TopicInfo]:
        """
        Return metadata for all discovered topics.
        """

        return list(
            self.topic_cache.values()
        )

    def get_topic(
        self,
        topic_id: int,
    ) -> TopicInfo:
        """
        Return metadata for a single topic.
        """

        try:

            return self.topic_cache[
                topic_id
            ]

        except KeyError as error:

            raise ValueError(
                f"Unknown topic: {topic_id}"
            ) from error


# =====================================================
# SINGLETON FACTORY
# =====================================================

@lru_cache(maxsize=4)
def get_topic_inference(
    model_path: str = str(
        DEFAULT_MODEL_PATH,
    ),
) -> TopicInference:
    """
    Return a cached TopicInference instance.

    Each unique model path is loaded only once.
    """

    return TopicInference(
        model_path=model_path,
    )


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Interactive BERTopic inference CLI.
    """

    inference = (
        get_topic_inference()
    )

    print("=" * 60)
    print("BERTopic Inference")
    print("=" * 60)

    health = inference.health()

    print(
        f"Model  : {health.model_version}"
    )

    print(
        f"Topics : {health.topic_count}"
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

            prediction = (
                inference.predict(
                    review,
                )
            )

            print()

            print("=" * 60)
            print("Topic Prediction")
            print("=" * 60)

            print(
                prediction.model_dump_json(
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