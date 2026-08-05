"""
=========================================================
RoBERTa Sentiment Inference
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Production inference module.

Responsibilities
----------------
1. Load trained model
2. Load tokenizer
3. Predict sentiment
4. Predict probabilities
5. Predict batch sentiment

This module MUST NOT:

- train models
- evaluate models
- compute metrics
- load DatasetDict
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Sequence

import torch
import torch.nn.functional as F

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from .schemas import SentimentPrediction


# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_MODEL = (
    BASE_DIR
    / "models"
    / "experiment_3"
)


# =====================================================
# CONFIGURATION
# =====================================================

MAX_LENGTH = 512


# =====================================================
# DEVICE
# =====================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# =====================================================
# SENTIMENT INFERENCE
# =====================================================

class SentimentInference:
    """
    Production sentiment inference service.

    The model is loaded once during initialization
    and reused for all predictions.
    """

    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL,
    ) -> None:

        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found:\n{model_path}"
            )

        self.model_path = model_path

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                model_path
            )
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(model_path)
        )

        self.model.to(DEVICE)
        self.model.eval()

        self.id2label = {
            int(key): value
            for key, value in self.model.config.id2label.items()
        }

        self.label2id = {
            value: key
            for key, value in self.id2label.items()
        }

    @property
    def version(self) -> str:
        """
        Model version.
        """

        return self.model_path.name

    def health(
        self,
    ) -> dict[str, object]:
        """
        Return service information.
        """

        return {
            "status": "ready",
            "model": self.version,
            "device": str(DEVICE),
            "labels": list(
                self.id2label.values()
            ),
        }

    def _tokenize(
        self,
        text: str,
    ) -> dict[str, torch.Tensor]:
        """
        Tokenize a single review.
        """

        text = text.strip()

        if not text:
            raise ValueError(
                "Input text cannot be empty."
            )

        encoded = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LENGTH,
        )

        return {
            key: value.to(DEVICE)
            for key, value in encoded.items()
        }

    def _build_prediction(
        self,
        probabilities: torch.Tensor,
    ) -> SentimentPrediction:
        """
        Convert probability tensor into
        SentimentPrediction.
        """

        confidence, label_id = torch.max(
            probabilities,
            dim=0,
        )

        label_id = int(label_id.item())

        scores = probabilities.cpu().tolist()

        probability_dict = {
            self.id2label[index]: float(score)
            for index, score in enumerate(scores)
        }

        return SentimentPrediction(
            label=self.id2label[label_id],
            label_id=label_id,
            confidence=float(
                confidence.item()
            ),
            probabilities=probability_dict,
            model_version=self.version,
        )

    @torch.inference_mode()
    def predict(
        self,
        text: str,
    ) -> SentimentPrediction:
        """
        Predict sentiment.
        """

        encoded = self._tokenize(
            text
        )

        outputs = self.model(
            **encoded
        )

        probabilities = F.softmax(
            outputs.logits.squeeze(0),
            dim=0,
        )

        return self._build_prediction(
            probabilities
        )

    @torch.inference_mode()
    def predict_proba(
        self,
        text: str,
    ) -> dict[str, float]:
        """
        Return only class probabilities.

        This method reuses ``predict()`` to avoid
        duplicating inference logic.
        """

        return self.predict(
            text
        ).probabilities

    @torch.inference_mode()
    def predict_batch(
        self,
        texts: Sequence[str],
    ) -> list[SentimentPrediction]:
        """
        Predict sentiment for multiple reviews.
        """

        reviews = [
            text.strip()
            for text in texts
        ]

        if not reviews:
            raise ValueError(
                "Input list cannot be empty."
            )

        if any(
            not review
            for review in reviews
        ):
            raise ValueError(
                "Input list contains empty reviews."
            )

        encoded = self.tokenizer(
            reviews,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
        )

        encoded = {
            key: value.to(DEVICE)
            for key, value in encoded.items()
        }

        outputs = self.model(
            **encoded
        )

        probabilities = F.softmax(
            outputs.logits,
            dim=1,
        )

        return [
            self._build_prediction(
                probs
            )
            for probs in probabilities
        ]

    def predict_label(
        self,
        text: str,
    ) -> str:
        """
        Predict only the sentiment label.
        """

        return self.predict(
            text
        ).label

    def predict_confidence(
        self,
        text: str,
    ) -> float:
        """
        Predict only the confidence score.
        """

        return self.predict(
            text
        ).confidence


# =====================================================
# SINGLETON FACTORY
# =====================================================

@lru_cache(maxsize=1)
def get_sentiment_inference(
    model_path: str = str(DEFAULT_MODEL),
) -> SentimentInference:
    """
    Return a cached inference service.

    Each unique model path is loaded only once.
    """

    return SentimentInference(
        model_path=model_path,
    )


# =====================================================
# MAIN
# =====================================================

def main() -> None:
    """
    Interactive inference CLI.
    """

    inference = get_sentiment_inference()

    print("=" * 60)
    print("RoBERTa Sentiment Inference")
    print("=" * 60)
    print(f"Model  : {inference.version}")
    print(f"Device : {DEVICE}")
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

            prediction = inference.predict(
                review
            )

            print()
            print("=" * 60)
            print("Prediction Summary")
            print("=" * 60)
            print(
                f"Label      : {prediction.label}"
            )
            print(
                f"Confidence : "
                f"{prediction.confidence:.4f}"
            )

            print("\nProbabilities")

            for (
                label,
                score,
            ) in prediction.probabilities.items():

                print(
                    f"  {label:<10}: "
                    f"{score:.4f}"
                )

            print("\nJSON Output")
            print("-" * 60)

            print(
                prediction.model_dump_json(
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