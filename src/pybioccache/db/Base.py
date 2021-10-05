from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

Base = declarative_base()

def create_schema(cache_dir): 
    if not cache_dir:
        raise Exception(f"cache_dir cannot be empty")

    engine = create_engine(f'sqlite:///{cache_dir}')
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    return (engine, SessionLocal)
