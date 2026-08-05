"""
Preprocessing package.

Expose the main preprocessing function so it can be
imported directly from the package.
"""

from .preprocess import preprocess_reviews

__all__ = [
    "preprocess_reviews"
]