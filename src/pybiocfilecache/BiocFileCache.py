"""
Python Implementation of BiocFileCache
"""

import logging
import sys
import os
import tempfile
import uuid

from pybiocfilecache import __version__
from .db import create_schema
from .db.schema import Resource
from shutil import copy2, move
from sqlalchemy import func

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


class BiocFileCache:
    """
    Class to manage and cache files
    """

    def __init__(self, cache_dir: str = None):
        # check if cache dir exists, if not use the tmp directory
        if cache_dir is None:
            self.cache = BiocFileCache.create_tmp_dir()
        else:
            if not os.path.isdir(cache_dir):
                mode = 0o777
                try:
                    os.mkdir(cache_dir, mode)
                except Exception as e:
                    raise Exception(
                        f"Failed to created directory {cache_dir}: {str(e)}"
                    )

            self.cache = cache_dir

        # create/access sqlite file
        db_cache = f"{self.cache}/BiocFileCache.sqlite"
        (self.engine, self.sessionLocal) = create_schema(db_cache)

    def add(
        self,
        rname: str,
        fpath: str,
        rtype: str = "local",
        action: str = "copy",
        ext: bool = False,
    ):
        """Add a resource to cache from a given name and path

        Args:
            rname (str): Name of the resource to add to cache
            fpath (str): Location of the resource
            rtype (str, optional): one of local, web, or relative. Defaults to "local".
            action (str, optional): either copy, move or asis. Defaults to "copy".
            ext (bool, optional): use file extension when storing in cache ? Defaults to False.

        Returns:
            database record of the new resource in cache
        """
        if not os.path.exists(fpath):
            raise Exception(f"File at {fpath} does not exist")

        existing_cache = self.get(rname)
        if existing_cache is not None:
            # raise Exception(f"File with {rname} already exists")
            _logger.info(f"File with {rname} already exists, updating instead")
            self.update(rname, fpath)
            return

        rid = BiocFileCache.generate_id()
        rbasename, rext = os.path.splitext(os.path.basename(fpath)[0])

        rpath = f"{self.cache}/{rid}.{rext}" if ext else f"{self.cache}/{rid}"

        # copy the file to cache
        try:
            if action == "copy":
                copy2(fpath, rpath)
            elif action == "move":
                move(fpath, rpath)
        except Exception as e:
            raise Exception(f"Error storing file in cache: {str(e)}")

        # create new record in the database
        res = Resource(
            **dict(rid=rid, rname=rname, rpath=rpath, rtype=rtype, fpath=fpath)
        )

        session = self.sessionLocal()
        session.add(res)
        session.commit()
        session.refresh(res)

        return res

    @staticmethod
    def create_tmp_dir():
        """create a temporary directory

        Returns:
            str: path to the directory
        """        
        return tempfile.mkdtemp()

    @staticmethod
    def generate_id():
        """Generate uuid

        Returns:
            str: unique string for use as id
        """        
        return uuid.uuid4().hex

    def query(self, query: str, field: str = "rname"):
        """Search cache for a resource

        Args:
            query (str): query to search
            field (str, optional): Field to search. Defaults to "rname".

        Returns:
            obj: list of matching resources from cache
        """
        session = self.sessionLocal()

        res = (
            session.query(Resource)
            .filter(Resource[field].ilike("%{}%".format(query)))
            .all()
        )
        return res

    def get(self, rname: str):
        """get resource by name from cache

        Args:
            rname (str): Name of the file to search

        Returns:
            Resource: matched resource from cache
        """
        session = self.sessionLocal()

        res = session.query(Resource).filter(Resource.rname == rname).first()
        return res

    def remove(self, rname: str):
        """remove a resource from cache

        Args:
            rname (str): resource to remove
        """
        session = self.sessionLocal()

        res = session.query(Resource).filter(Resource.rname == rname).first()
        session.delete(res)
        session.commit()

        # remove file
        os.remove(res.rpath)

    def purge(self):
        """Remove all files from cache"""
        for file in os.scandir(self.cache):
            os.remove(file.path)

    def update(self, rname: str, fpath: str, action: str = "copy"):
        """Update a resource in cache

        Args:
            rname (str): name of the resource in cache
            fpath (str): new resource to replace existing file in cache

        Returns:
            Resource: Updated resource record in cache
        """
        session = self.sessionLocal()

        if not os.path.exists(fpath):
            raise Exception(f"File at {fpath} does not exist")

        # get current record
        rec = self.get(rname)

        # copy the file to cache
        try:
            if action == "copy":
                copy2(fpath, rec.rpath)
            elif action == "move":
                move(fpath, rec.rpath)
        except Exception as e:
            raise Exception(f"Error storing file in cache: {str(e)}")

        rec.create_time = rec.access_time = rec.last_modified_time = func.now()

        session.add(rec)
        session.commit()
        session.refresh(rec)
        return rec


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )
