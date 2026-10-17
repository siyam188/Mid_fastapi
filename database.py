
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLACHEMY_DATABASE_URL = os.getenv("SQLACHEMY_DATABASE_URL")

if not SQLACHEMY_DATABASE_URL:
    raise RuntimeError("Database URL is not set")

engine = create_engine(SQLACHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()
