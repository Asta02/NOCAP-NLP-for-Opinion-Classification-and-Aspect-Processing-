"""
Database configuration.

Responsibilities:
- Database credentials
- SQLAlchemy database URL
- Engine settings
"""

DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DATABASE_NAME = "employee_feedback"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "12345678"

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

# SQLAlchemy engine settings
DATABASE_ECHO = False

DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 1800