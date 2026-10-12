from sqlalchemy import text
from app.database.database import SessionLocal, engine


def test_engine():
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT NOW(), current_database(), current_user")
        ).one()
        print("Engine OK:", row)


def test_session():
    db = SessionLocal()
    try:
        print("Session OK:", db.execute(text("SELECT 1")).scalar())
    finally:
        db.close()


if __name__ == "__main__":
    try:
        test_engine()
        test_session()
        print("Database connection successful")
    except Exception as e:
        print("Database connection failed:")
        print(e)