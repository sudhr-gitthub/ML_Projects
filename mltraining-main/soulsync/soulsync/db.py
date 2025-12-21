import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DEFAULT_DB = "sqlite:///phantom_life.db"

def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DB)

def make_engine(echo: bool = False):
    url = get_database_url()
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(url, echo=echo, future=True, connect_args=connect_args)

_ENGINE = make_engine(echo=False)
SessionLocal = scoped_session(sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False, future=True))
def get_session():
    return SessionLocal()

def init_db(Base):
    Base.metadata.create_all(bind=_ENGINE)
