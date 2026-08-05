"""
=========================================================
BERTopic Trainer
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Train and save BERTopic models.

Responsibilities
----------------
1. Prepare training documents
2. Build BERTopic pipeline
3. Train BERTopic
4. Save trained model
5. Return training summary
"""

from __future__ import annotations

import logging
import random
from pathlib import Path

import numpy as np
from bertopic import BERTopic
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP

from .constants import (
    DEFAULT_MODEL_PATH,
    EMBEDDING_MODEL,
    HDBSCAN_CONFIG,
    MODEL_CONFIG,
    RANDOM_STATE,
    TOPIC_CONFIG,
    UMAP_CONFIG,
    VECTORIZER_CONFIG,
)
from .preprocessing import prepare_training_documents
from .schemas import TopicTrainingSummary

LOGGER = logging.getLogger(__name__)

random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)


class BERTopicTrainer:
    """
    BERTopic training service.
    """

    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
    ) -> None:

        self.model_path = Path(model_path)

        self.embedding_model = self._build_embedding_model()
        self.umap_model = self._build_umap()
        self.hdbscan_model = self._build_hdbscan()
        self.vectorizer_model = self._build_vectorizer()

        self.model = self._build_topic_model()

    @property
    def version(self) -> str:
        return MODEL_CONFIG["version"]

    # =================================================
    # BUILDERS
    # =================================================

    def _build_embedding_model(
        self,
    ) -> SentenceTransformer:
        """
        Build embedding model.
        """

        LOGGER.info("Loading embedding model...")

        return SentenceTransformer(
            EMBEDDING_MODEL
        )

    def _build_umap(
        self,
    ) -> UMAP:
        """
        Build UMAP model.
        """

        return UMAP(
            **UMAP_CONFIG,
        )

    def _build_hdbscan(
        self,
    ) -> HDBSCAN:
        """
        Build HDBSCAN model.
        """

        return HDBSCAN(
            **HDBSCAN_CONFIG,
        )

    def _build_vectorizer(
        self,
    ) -> CountVectorizer:
        """
        Build CountVectorizer.
        """

        return CountVectorizer(
            **VECTORIZER_CONFIG,
        )

    def _build_topic_model(
        self,
    ) -> BERTopic:
        """
        Build BERTopic model.
        """

        return BERTopic(
            embedding_model=self.embedding_model,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan_model,
            vectorizer_model=self.vectorizer_model,
            **TOPIC_CONFIG,
        )

    # =================================================
    # PUBLIC API
    # =================================================

    def train(
        self,
    ) -> TopicTrainingSummary:
        """
        Train BERTopic using the prepared
        training documents.
        """

        LOGGER.info(
            "Loading training documents..."
        )

        documents = (
            prepare_training_documents()
        )

        LOGGER.info(
            "Training BERTopic on %d documents...",
            len(documents),
        )

        topics, _ = self.model.fit_transform(
            documents
        )

        topic_info = self.model.get_topic_info()

        outlier_count = int(
            (topic_info.Topic == -1).sum()
        )

        topic_count = len(
            topic_info[
                topic_info.Topic != -1
            ]
        )

        LOGGER.info(
            "Discovered %d topics (%d outliers).",
            topic_count,
            outlier_count,
        )

        LOGGER.info(
            "Training completed."
        )

        return TopicTrainingSummary(
            model_version=MODEL_CONFIG["version"],
            document_count=len(documents),
            topic_count=topic_count,
            outlier_count=outlier_count,
            embedding_model=EMBEDDING_MODEL,
            saved_model_path=str(
                self.model_path.resolve()
            ),
        )

    def save(
        self,
    ) -> None:
        """
        Save the trained BERTopic model.
        """

        LOGGER.info(
            "Saving BERTopic model..."
        )

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.model.save(
            self.model_path,
            save_embedding_model=MODEL_CONFIG[
                "save_embedding_model"
            ],
        )

        LOGGER.info(
            "Model saved to:\n%s",
            self.model_path,
        )

    def train_and_save(
        self,
    ) -> TopicTrainingSummary:
        """
        Train and save BERTopic.
        """

        summary = self.train()

        self.save()

        return summary


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Train BERTopic from the command line.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    trainer = BERTopicTrainer()

    print("=" * 60)
    print("BERTopic Trainer")
    print("=" * 60)

    try:

        summary = (
            trainer.train_and_save()
        )

        print()

        print("=" * 60)
        print("Training Summary")
        print("=" * 60)

        print(
            summary.model_dump_json(
                indent=4,
            )
        )

        print("=" * 60)

    except KeyboardInterrupt:

        print("\nTraining cancelled.")

    except Exception as error:

        LOGGER.exception(
            "Training failed."
        )

        print(
            f"\nError: {error}"
        )


if __name__ == "__main__":
    main()