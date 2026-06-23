import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Respeta DATABASE_URL del entorno (en Docker apunta al volumen /data para que
# la base persista entre rebuilds). Sin la variable, usa el archivo local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plomeria.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
