"""
Python Implementation of BiocFileCache
"""

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

class NoFpathError(Exception):
    """An error for when the source file does not exist."""


class RnameExistsError(Exception):
    """An error for when the key already exists in the cache."""


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

        Raises:
            NoFpathError
                When the `fpath` does not exist.
            RnameExistsError
                When the `rname` already exists in the cache.
            sqlalchemy exceptions
                When something is up with the cache.
        """
        if isinstance(fpath, str):
            fpath = Path(fpath)

        if not fpath.exists():
            raise NoFpathError(f"Resource at {fpath} does not exist.")

        rid = generate_id()
        rpath = f"{self.cache}/{rid}" + (f".{fpath.suffix}" if ext else "")

        # create new record in the database
        res = Resource(
            **dict(
                rid=rid,
                rname=rname,
                rpath=rpath,
                rtype=rtype,
                fpath=str(fpath),
            )
        )

        # If this was higher up a parallel process could have added the key to
        # the cache in the meantime as the above takes a bit, so checking here
        # reduces the odds of this happening
        # Redirecting to update was removed as it is a scenario better handled
        # by the caller.
        if self.get(rname) is not None:
            raise RnameExistsError("Resource already exists in cache!")

        with self.sessionLocal() as session:
            session.add(res)  # type: ignore
            session.commit()
            session.refresh(res)  # type: ignore

        # In the "move" scenario if we move the file to rpath before rpath is
        # part of the cache and then when trying to add it to the cache an
        # exception is raised (such as if it is locked by another process) the
        # data essentially disappears to rpath with no way of retrieving its
        # location. Thus we add rpath to the cache first, then move the data
        # into it so that the data at source does not disappear if accessing
        # the cache raises an exception.
        copy_or_move(str(fpath), rpath, rname, action)

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
