import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# En local toma el default; en Docker se inyecta DATABASE_URL (ver docker-compose.yml),
# apuntando al volumen persistente (sqlite:////data/plomeria.db).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plomeria.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
