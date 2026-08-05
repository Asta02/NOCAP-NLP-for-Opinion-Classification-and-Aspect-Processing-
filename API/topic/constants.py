"""
=========================================================
BERTopic Constants
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Shared configuration for BERTopic training
and inference.
"""

from __future__ import annotations

from pathlib import Path

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"

DEFAULT_MODEL_NAME = "bertopic_v1.pkl"

DEFAULT_MODEL_PATH = MODEL_DIR / DEFAULT_MODEL_NAME

# =====================================================
# DATA
# =====================================================

TEXT_COLUMNS = (
    "cleaned_review",
    "sentiment_text",
    "review",
)

DEFAULT_LANGUAGE = "english"

# =====================================================
# PREPROCESSING
# =====================================================

PREPROCESSING_CONFIG: dict[str, object] = {
    "remove_duplicates": True,
    "min_document_length": 5,
}

# =====================================================
# EMBEDDING
# =====================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# =====================================================
# UMAP
# =====================================================

UMAP_CONFIG: dict[str, object] = {
    "n_neighbors": 15,
    "n_components": 5,
    "min_dist": 0.0,
    "metric": "cosine",
    "random_state": 42,
}

# =====================================================
# HDBSCAN
# =====================================================

HDBSCAN_CONFIG: dict[str, object] = {
    "min_cluster_size": 15,
    "min_samples": 10,
    "metric": "euclidean",
    "prediction_data": True,
}

# =====================================================
# COUNT VECTORIZER
# =====================================================

VECTORIZER_CONFIG: dict[str, object] = {
    "stop_words": DEFAULT_LANGUAGE,
    "ngram_range": (1, 2),
    "min_df": 5,
}

# =====================================================
# BERTopic
# =====================================================

TOPIC_CONFIG: dict[str, object] = {
    "calculate_probabilities": True,
    "verbose": True,
    "top_n_words": 10,
}

# =====================================================
# MODEL
# =====================================================

MODEL_CONFIG: dict[str, object] = {
    "name": DEFAULT_MODEL_NAME,
    "version": "bertopic_v1",
    "description": (
        "BERTopic using MiniLM embeddings "
        "for employee review topic modeling."
    ),
    "save_embedding_model": True,
}

SAVE_EMBEDDING_MODEL = True

# =====================================================
# MISC
# =====================================================

OUTLIER_TOPIC_ID = -1

RANDOM_STATE = 42