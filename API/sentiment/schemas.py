from pydantic import BaseModel, Field


class SentimentPrediction(BaseModel):
    """
    Sentiment prediction result.
    """

    label: str

    label_id: int

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    probabilities: dict[str, float]

    model_version: str