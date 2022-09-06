from typing import Tuple

from sqlalchemy import create_engine  # type: ignore
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from .utils import StrPath

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


# TODO: this is built every time this module is run which seems inefficient,
# there has to be a better way...
Base = declarative_base()


def create_schema(cache_dir: StrPath) -> Tuple[Engine, sessionmaker]:
    """Create the schema in the sqlite database.

    Parameters
    ----------
    cache_dir : Path | str
        Path to the sqlite database.

    Returns
    -------
    engine : Engine
        An sqlalchemy `Engine` object.
    local_session_maker : sessionmaker
        An sqlalchemy `sessionmaker` object.
    """
    engine = create_engine(
        f"sqlite:///{cache_dir}", connect_args={"check_same_thread": False}
    )
    local_session_maker = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Base.metadata.create_all(engine)
    return (engine, local_session_maker)


# TODO: should return base types instead of column type when accessing an
# attribute...


class Metadata(Base):
    """Class for holding a resource's metadata."""

    __tablename__ = "metadata"
    key = Column(String(), primary_key=True, index=True)
    value = Column(String())

    def __repr__(self):
        """Represent the object as a `str`."""
        return f"<Metadata(key='{self.key}', value='{self.value}')>"


class Resource(Base):
    """Class for holding a resource's data."""

    __tablename__ = "resource"
    access_time = Column(DateTime, server_default=func.now())
    create_time = Column(DateTime, server_default=func.now())
    e_tag = Column(String())
    expires = Column(DateTime)
    f_path = Column(String())
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    last_modified_time = Column(DateTime, onupdate=func.now())
    r_id = Column(String())
    r_name = Column(String())
    r_path = Column(String())
    r_type = Column(String())

    def __repr__(self):
        """Represent the object as a `str`."""
        return f"<Resource(id='{self.id}', r_name='{self.r_name}')>"
