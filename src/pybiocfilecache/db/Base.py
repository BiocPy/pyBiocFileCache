from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Tuple

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

Base = declarative_base()


def create_schema(cache_dir: str) -> Tuple[Engine, sessionmaker]:
    """Create the schema in the sqlite database

    Args:
        cache_dir (str): Location where the cache directory

    Returns:
        a tuple of sqlalchemy engine and session maker
    """

    engine = create_engine(
        f"sqlite:///{cache_dir}", connect_args={"check_same_thread": False}
    )
    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    return (engine, sessionLocal)
