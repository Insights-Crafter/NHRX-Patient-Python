# app/db/database.py
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

# URL.create() escapes special characters in the password for you
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME"),
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
    pass


def get_db():
    """FastAPI dependency: opens a session, yields it, always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()