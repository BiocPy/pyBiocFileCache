from typing import Tuple

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

Base = declarative_base()


def create_schema(cache_dir: str) -> Tuple[Engine, sessionmaker]:
    """Create the schema in the sqlite database.

    Args:
        cache_dir:
            Location where the cache directory.

    Returns:
        A tuple of sqlalchemy engine and session maker.
    """
    try:
        engine = create_engine(
            f"sqlite:///{cache_dir}", connect_args={"check_same_thread": False}
        )

        Base.metadata.create_all(bind=engine, checkfirst=True)
        sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        return (engine, sessionLocal)
    except Exception as e:
        raise e
