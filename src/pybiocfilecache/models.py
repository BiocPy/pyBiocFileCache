from sqlalchemy import Column, DateTime, Integer, Text, func
from sqlalchemy.orm import declarative_base

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"

Base = declarative_base()


class Metadata(Base):
    """Database metadata information."""

    __tablename__ = "metadata"

    key = Column(Text(), primary_key=True, index=True, unique=True)
    value = Column(Text())

    def __repr__(self) -> str:
        return f"<Metadata(key='{self.key}', value='{self.value}')>"

    def to_dict(self) -> dict:
        return {"key": self.key, "value": self.value}


class Resource(Base):
    """Resource information stored in cache.

    Attributes:
        id:
            Auto-incrementing primary key.

        rid:
            Unique resource identifier (UUID).

        rname:
            User-provided resource name.

        create_time:
            When the resource was first added.

        access_time:
            Last time the resource was accessed.

        rpath:
            Path to the resource in the cache.

        rtype:
            Type of resource (local, web, relative).

        fpath:
            Original file path.

        last_modified_time:
            Last time the resource was modified.

        etag:
            Checksum/hash of the resource.

        expires:
            When the resource should be considered expired.
    """

    __tablename__ = "resource"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rid = Column(Text())
    rname = Column(Text())
    create_time = Column(DateTime, server_default=func.now())
    access_time = Column(DateTime, server_default=func.now())
    rpath = Column(Text())
    rtype = Column(Text())
    fpath = Column(Text())
    last_modified_time = Column(DateTime, onupdate=func.now(), default=None)
    etag = Column(Text(), default=None)
    expires = Column(DateTime, default=None)

    def __repr__(self) -> str:
        return f"<Resource(rid='{self.rid}', rname='{self.rname}', rpath='{self.rpath}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "rid": self.rid,
            "rname": self.rname,
            "create_time": self.create_time,
            "access_time": self.access_time,
            "rpath": self.rpath,
            "rtype": self.rtype,
            "fpath": self.fpath,
            "last_modified_time": self.last_modified_time,
            "etag": self.etag,
            "expires": self.expires,
        }
