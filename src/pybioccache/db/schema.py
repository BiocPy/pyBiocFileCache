from .Base import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
import logging

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class Metadata(Base):
    __tablename__ = 'metadata'
    key = Column(String(), primary_key=True, index=True)
    value = Column(String())

    def __repr__(self):
        return "<Metadata(key='%s', valye='%s')>" % (self.key, self.value)

class Resource(Base):
    __tablename__ = 'resource'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rid = Column(String())
    rname = Column(String())
    create_time = Column(DateTime, server_default=func.now())
    access_time = Column(DateTime, server_default=func.now())
    rpath = Column(String())
    rtype = Column(String())
    fpath = Column(String())

    last_modified_time = Column(DateTime, onupdate=func.now())
    etag = Column(String())
    expires = Column(DateTime)

    def __repr__(self):
        return "<Resource(id='%s', rname='%s')>" % (self.id, self.rname)