"""
Python Implementation of BiocFileCache
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from sqlalchemy import func
from sqlalchemy.orm import Session

from .db import create_schema
from .db.schema import Resource
from .utils import copy_or_move, create_tmp_dir, generate_id

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


class BiocFileCache:
    """
    Class to manage and cache files.
    """

    def __init__(self, cacheDirOrPath: Union[str, Path] = create_tmp_dir()):
        """Initialize BiocFileCache.

        Args:
            cacheDirOrPath (Union[str, Path], optional): Path to cache
                directory. Defaults to tmp location, `create_tmp_dir()`.

        Raises:
            Exception: Failed to initialize cache.
        """
        if isinstance(cacheDirOrPath, str):
            cacheDirOrPath = Path(cacheDirOrPath)

        if not cacheDirOrPath.exists():
            mode = 0o777
            try:
                cacheDirOrPath.mkdir(mode=mode, parents=True, exist_ok=True)
            except Exception as e:
                raise Exception(f"Failed to created directory {cacheDirOrPath}") from e

        self.cache = str(cacheDirOrPath)

        # create/access sqlite file
        self.db_cache = f"{self.cache}/BiocFileCache.sqlite"
        (self.engine, self.sessionLocal) = create_schema(self.db_cache)

    def add(
        self,
        rname: str,
        fpath: Union[str, Path],
        rtype: str = "local",
        action: str = "copy",
        ext: bool = False,
    ) -> Resource:
        """Add a resource from the provided `fpath` to cache as `rname`.

        Args:
            rname (str): Name of the resource to add to cache.
            fpath (Union[str, Path]): Location of the resource.
            rtype (str, optional): One of `local`, `web`, or `relative`.
                Defaults to `"local"`.
            action (str, optional): Either `copy`, `move` or `asis`.
                Defaults to `"copy"`.
            ext (bool, optional): Use filepath extension when storing in cache.
                Defaults to `False`.

        Returns:
            Resource: Database record of the new resource in cache
        """

        if isinstance(fpath, str):
            fpath = Path(fpath)

        if not fpath.exists():
            raise Exception(f"Resource at {fpath} does not exist.")

        existing_cache = self.get(rname)
        if existing_cache is not None:
            _logger.info(f"File with {rname} already exists, updating instead")
            return self.update(rname, fpath, action)

        rid = generate_id()
        rpath = f"{self.cache}/{rid}.{fpath.suffix}" if ext else f"{self.cache}/{rid}"

        copy_or_move(str(fpath), rpath, rname, action)

        # create new record in the database
        res = Resource(
            **dict(rid=rid, rname=rname, rpath=rpath, rtype=rtype, fpath=str(fpath))
        )

        with self.sessionLocal() as session:
            session.add(res)
            session.commit()
            session.refresh(res)

        return res

    def query(self, query: str, field: str = "rname") -> List[Resource]:
        """Search cache for a resource.

        Args:
            query (str): query to search
            field (str, optional): Field to search. Defaults to "rname".

        Returns:
            List[Resource]: list of matching resources from cache
        """
        with self.sessionLocal() as session:
            return (
                session.query(Resource)
                .filter(Resource[field].ilike("%{}%".format(query)))
                .all()
            )

    def _get(self, session: Session, rname: str) -> Optional[Resource]:
        """Get a resource with `rname` from given `Session`.

        Args:
            session (Session): The `Session` object to use.
            rname (str): The `rname` of the `Resource` to get.

        Returns:
            res (Resource, optional): The `Resource` for the `rname` if any.
        """
        return session.query(Resource).filter(Resource.rname == rname).first()

    def get(self, rname: str) -> Optional[Resource]:
        """get resource by name from cache.

        Args:
            rname (str): Name of the file to search

        Returns:
            Optional[Resource]: matched resource from cache if exists.
        """
        return self._get(self.sessionLocal(), rname)

    def remove(self, rname: str) -> None:
        """Remove a resource from cache by name.

        Args:
            rname (str): Name of the resource to remove
        """
        with self.sessionLocal() as session:
            res: Resource = self._get(session, rname)
            session.delete(res)
            session.commit()
            # remove file
            Path(res.rpath).unlink()

    def purge(self):
        """Remove all files from cache."""
        for file in os.scandir(self.cache):
            os.remove(file.path)

    def update(
        self, rname: str, fpath: Union[str, Path], action: str = "copy"
    ) -> Resource:
        """Update a resource in cache.

        Args:
            rname (str): name of the resource in cache
            fpath (Union[str, Path]): new resource to replace existing file in cache.
            action (str, optional): either copy of move. defaults to copy

        Returns:
            Resource: Updated resource record in cache
        """

        if isinstance(fpath, str):
            fpath = Path(fpath)

        if not fpath.exists():
            raise Exception(f"File: '{fpath}' does not exist")

        with self.sessionLocal() as session:
            res: Resource = self._get(session, rname)
            # copy the file to cache
            copy_or_move(str(fpath), str(res.rpath), rname, action)
            # TODO: is this needed?
            res.create_time = res.access_time = res.last_modified_time = func.now()
            session.merge(res)
            session.commit()
            session.refresh(res)

        return res
