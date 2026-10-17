from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLACHEMY_DATABASE_URL = "postgresql://postgres.vslyefzauiclmznqtkbz:siyamdb1245@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

engine = create_engine(
    SQLACHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()