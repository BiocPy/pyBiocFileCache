"""The BiocFileCache class."""

from logging import getLogger
from pathlib import Path
from shutil import copy2, move
from tempfile import mkdtemp
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func

from .db import Resource, create_schema
from .utils import StrPath

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

_logger = getLogger(__name__)


class BiocFileCache:
    """Manage and cache files."""

    def __init__(self, cache_dir: StrPath = mkdtemp()) -> None:
        """Initialize BiocFileCache.

        Parameters
        ----------
        cache_dir : Path | str
            The path to the cache directory. Default = `mkdtemp()`.
        """
        if isinstance(cache_dir, str):
            cache_dir = Path(cache_dir)

        if not cache_dir.exists():
            try:
                cache_dir.mkdir(parents=True)
            except Exception as expt:
                raise Exception(
                    f"Failed to create directory: '{cache_dir}'."
                ) from expt

        self.cache_dir = cache_dir

        # create/access sqlite file
        (self.engine, self.session_local) = create_schema(
            f"{self.cache_dir}/BiocFileCache.sqlite"
        )

    # TODO: add asis action?
    @staticmethod
    def _copy_or_move(
        action: str, fpath: StrPath, rpath: StrPath, rname: str
    ) -> None:
        """Try to copy or move the `fpath` to the `rpath`.

        Parameters
        ----------
        action : str
            Either `"copy"` or `"move"`. Default = `"copy"`.
        fpath : Path | str
            Location of the resource to copy or move.
        rpath : str
            Destination to copy or move to.
        rname :  str
            Name of the resource to add to cache.
        """
        try:
            if action == "copy":
                copy2(fpath, rpath)
            elif action == "move":
                move(str(fpath), rpath)
        except Exception as expt:
            if action not in ["copy", "move"]:
                raise Exception(
                    f"Given action: {action} not one of 'move' or 'copy'."
                ) from expt

            raise Exception(
                f"Error storing resource: '{rname}' from: '{rpath}' in "
                "cache.",
            ) from expt

    def add(  # pylint: disable=too-many-arguments
        self,
        rname: str,
        fpath: StrPath,
        rtype: str = "local",
        action: str = "copy",
        ext: bool = False,
    ) -> Resource:
        """Add the file at `fpath` to the cache under `rname`.

        Parameters
        ----------
        rname :  str
            Name of the resource to add to cache.
        fpath : Path | str
            Location of the resource to add to the cache.
        rtype : str
            One of `"local"`, `"web"`, or `"relative"`. Default = `"local"`.
        action : str
            Either `"copy"` or `"move"`. Default = `"copy"`.
        ext : bool
            Use file extension when storing in cache? Default = `False`.

        Returns
        -------
        resource : Resource
            The `Resource` object containing the new resource.
        """
        if isinstance(fpath, str):
            fpath = Path(fpath)

        if not fpath.exists():
            raise Exception(f"Resource at {fpath} does not exist.")

        if self.get(rname) is not None:
            _logger.info(
                "File with name '%s' already exists in cache, updating "
                "instead.",
                rname,
            )
            return self.update(rname, fpath)

        rid = uuid4().hex

        rpath = (
            f"{self.cache_dir}/{rid}.{fpath.suffix}"
            if ext
            else f"{self.cache_dir}/{rid}"
        )

        # copy the file to cache
        self._copy_or_move(action, fpath, rpath, rname)

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

        with self.session_local() as session:
            session.add(res)  # type: ignore
            session.commit()
            session.refresh(res)  # type: ignore

        return res

    def query(self, query: str, field: str = "rname") -> List[Resource]:
        """Search cache for a resource.

        Parameters
        ----------
        query : str
            Query to search for.
        Field : str
            Field to search, one of `"access_time"`, ``"create_time"`,
            `"etag"`, `"expires"`, `"fpath"`, "id"`, `"last_modified_time"`,
            `"rid"`, `"rname"`, `"rpath"`, `"rtype"`. Default = `"rname"`.

        Returns
        -------
        resource_list : List[Resource]
            A `list` of matching resource from the cache.
        """
        with self.session_local() as session:
            return (
                session.query(Resource)
                .filter(Resource[field].ilike(f"%{query}%"))  # type: ignore
                .all()
            )

    def get(self, rname: str) -> Optional[Resource]:
        """Get a resource by `rname` from the cache if it exists.

        Parameters
        ----------
        rname : str
            The `rname` of the file to search.

        Returns
        -------
        resource : Resource | None
            The matching `Resource` object from the cache if it exists.
        """
        with self.session_local() as session:
            return (
                session.query(Resource)
                .filter_by(rname=rname)  # type: ignore
                .first()
            )

    def remove(self, rname: str) -> None:
        """Remove a `Resource` from the cache by `rname`.

        Parameters
        ----------
        rname : str
            The `rname` of the resource to remove.
        """
        with self.session_local() as session:
            res: Resource = (
                session.query(Resource)
                .filter(Resource.rname == rname)  # type: ignore
                .first()
            )
            session.delete(res)  # type: ignore
            session.commit()

        # remove file
        Path(str(res.rpath)).unlink()

    def purge(self):
        """Remove all files from cache."""
        with self.session_local() as session:
            session.query(Resource).delete()
            session.commit()

    def update(
        self, rname: str, fpath: StrPath, action: str = "copy"
    ) -> Resource:
        """Update a resource in the cache.

        Parameters
        ----------
        rname : str
            The `rname` of the resource in cache.
        fpath : str | Path
            The path to the new file to replace the existing one in the cache.
        action : str
            Either `"copy"` or `"move"`. Default = `"copy"`.

        Returns
        -------
        resource : Resource
            The updated cache `Resource` containing the new file.
        """
        if isinstance(fpath, str):
            fpath = Path(fpath)

        if not fpath.exists():
            raise Exception(f"File: '{fpath}' does not exist")

        # get current record
        res = self.get(rname)

        if res is None:
            _logger.info(
                "File with name '%s' does not exist, adding instead using "
                "default arguments except 'action'.",
                rname,
            )
            return self.add(rname, fpath, action=action)

        # copy the file to cache
        self._copy_or_move(action, fpath, str(res.rpath), rname)

        res.create_time = res.access_time = res.last_modified_time = func.now()

        with self.session_local() as session:
            session.add(res)  # type: ignore
            session.commit()
            session.refresh(res)  # type: ignore

        return res
