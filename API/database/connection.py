from sqlalchemy import create_engine

from database.config import (
    DATABASE_URL,
    DATABASE_ECHO,
    DATABASE_POOL_SIZE,
    DATABASE_MAX_OVERFLOW,
    DATABASE_POOL_TIMEOUT,
    DATABASE_POOL_RECYCLE,
)

engine = create_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,
    pool_size=DATABASE_POOL_SIZE,
    max_overflow=DATABASE_MAX_OVERFLOW,
    pool_timeout=DATABASE_POOL_TIMEOUT,
    pool_recycle=DATABASE_POOL_RECYCLE,
)