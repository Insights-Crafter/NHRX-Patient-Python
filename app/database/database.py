# app/db/database.py
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

required_vars = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME")
missing_vars = [name for name in required_vars if not os.getenv(name)]
if missing_vars:
    raise RuntimeError("Missing database environment variable(s): " + ", ".join(missing_vars))

# URL.create() escapes special characters in the password for you
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME"),
    query={
        key: value
        for key, value in (
            ("sslmode", os.getenv("PGSSLMODE")),
            ("channel_binding", os.getenv("PGCHANNELBINDING")),
        )
        if value
    },
)

# One engine for the whole app (it manages the connection pool)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  
    pool_size=10,
    max_overflow=20,
    echo=False,         
)

# Factory that creates a new session per request
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """All models inherit from this."""
    # Neon pooler connections can reject search_path startup options, so
    # qualify ORM table references with the application's schema directly.
    metadata = MetaData(schema="public")


def get_db():
    """FastAPI dependency: opens a session, yields it, always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
