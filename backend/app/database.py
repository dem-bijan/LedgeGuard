import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session




load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

_url = (
    f"postgresql+psycopg://{os.environ['POSTGRES_USER']}:"
    f"{os.environ['POSTGRES_PASSWORD']}@localhost:5432/{os.environ['POSTGRES_DB']}"
)
engine = create_engine(_url)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()