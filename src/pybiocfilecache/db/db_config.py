from typing import Tuple

from sqlalchemy import create_engine, select, Column, Integer, Text, DateTime, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session

from sqlalchemy.orm import declarative_base, sessionmaker

from ..const import SCHEMA_VERSION

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

Base = declarative_base()


class Metadata(Base):
    __tablename__ = "metadata"
    key = Column(Text(), primary_key=True, index=True)
    value = Column(Text())

    def __repr__(self):
        return "<Metadata(key='%s', valye='%s')>" % (self.key, self.value)


class Resource(Base):
    __tablename__ = "resource"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rid = Column(Text())
    rname = Column(Text())
    create_time = Column(DateTime, server_default=func.now())
    access_time = Column(DateTime, server_default=func.now())
    rpath = Column(Text())
    rtype = Column(Text())
    fpath = Column(Text())
    last_modified_time = Column(DateTime, onupdate=func.now())
    etag = Column(Text())
    expires = Column(DateTime)

    def __repr__(self):
        return "<Resource(id='%s', rname='%s')>" % (self.id, self.rname)


def add_metadata(key: str, value: str, engine: Engine) -> None:
    """Add metadata to the database.

    Args:
        key:
            Key of the metadata.
        value:
            Value of the metadata.
        engine:
            Engine
    """
    with Session(engine) as session:
        if session.scalar(select(Metadata).where(Metadata.key == key)):
            pass
        else:
            new_metadata = Metadata(key=key, value=value)
            session.add(new_metadata)
            session.commit()


def create_schema(cache_dir: str) -> Tuple[Engine, sessionmaker]:
    """Create the schema in the sqlite database.

    Args:
        cache_dir:
            Location where the cache directory.

    Returns:
        A tuple of sqlalchemy engine and session maker.
    """
    engine = create_engine(
        f"sqlite:///{cache_dir}", connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(bind=engine, checkfirst=True)
    sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    add_metadata("schema_version", SCHEMA_VERSION, engine)

    return (engine, sessionLocal)
