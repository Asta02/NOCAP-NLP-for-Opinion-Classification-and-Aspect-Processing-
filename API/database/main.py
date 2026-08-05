"""
=========================================================
Database Initialization
=========================================================

Author  : Athar Winda
Project : NLP for Opinion Classification and Aspect Processing

Description
-----------
Initialize the PostgreSQL database.
"""

from __future__ import annotations

from database import models        # Registers all ORM models

from .base import Base
from .connection import engine


def main() -> None:

    print("=" * 60)
    print("Initializing Database")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully.")

    print("=" * 60)


if __name__ == "__main__":
    main()