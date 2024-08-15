from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:mysecretpassword@localhost:5432/contacts_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine, future=True)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
