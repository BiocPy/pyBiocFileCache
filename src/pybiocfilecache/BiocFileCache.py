"""The BiocFileCache class."""

from logging import getLogger
from pathlib import Path
from shutil import copy2, move
from tempfile import mkdtemp
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func

from .schema import Resource, create_schema
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

    @staticmethod
    def _copy_or_move(
        action: str, f_path: StrPath, r_path: StrPath, r_name: str
    ) -> None:
        """Try to copy or move the `f_path` to the `r_path`.

        Parameters
        ----------
        action : str
            Either `"copy"` or `"move"`. Default = `"copy"`.
        f_path : Path | str
            Location of the resource to copy or move.
        r_path : str
            Destination to copy or move to.
        r_name :  str
            Name of the resource to add to cache.
        """
        try:
            if action == "copy":
                copy2(f_path, r_path)
            elif action == "move":
                move(str(f_path), r_path)
        except Exception as expt:
            if action not in ["copy", "move"]:
                raise Exception(
                    f"Given action: {action} not one of 'move' or 'copy'."
                ) from expt

            raise Exception(
                f"Error storing resource: '{r_name}' from: '{r_path}' in "
                "cache.",
            ) from expt

    def add(  # pylint: disable=too-many-arguments
        self,
        r_name: str,
        f_path: StrPath,
        r_type: str = "local",
        action: str = "copy",
        ext: bool = False,
    ) -> Resource:
        """Add the file at `f_path` to the cache under `r_name`.

        Parameters
        ----------
        r_name :  str
            Name of the resource to add to cache.
        f_path : Path | str
            Location of the resource.
        r_type : str
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
        if isinstance(f_path, str):
            f_path = Path(f_path)

        if not f_path.exists():
            raise Exception(f"Resource at {f_path} does not exist.")

        if self.get(r_name) is not None:
            _logger.info(
                "File with name '%s' already exists in cache, updating "
                "instead.",
                r_name,
            )
            return self.update(r_name, f_path)

        r_id = uuid4().hex

        r_path = (
            f"{self.cache_dir}/{r_id}.{f_path.suffix}"
            if ext
            else f"{self.cache_dir}/{r_id}"
        )

        # copy the file to cache
        self._copy_or_move(action, f_path, r_path, r_name)

        # create new record in the database
        res = Resource(
            **dict(
                r_id=r_id,
                r_name=r_name,
                r_path=r_path,
                r_type=r_type,
                f_path=f_path,
            )
        )

        session = self.session_local()
        session.add(res)  # type: ignore
        session.commit()
        session.refresh(res)  # type: ignore

        return res

    def query(self, query: str, field: str = "r_name") -> List[Resource]:
        """Search cache for a resource.

        Parameters
        ----------
        query : str
            Query to search for.
        Field : str
            Field to search, one of `"access_time"`, ``"create_time"`,
            `"e_tag"`, `"expires"`, `"f_path"`, "id"`, `"last_modified_time"`,
            `"r_id"`, `"r_name"`, `"r_path"`, `"r_type"`. Default = `"r_name"`.

        Returns
        -------
        resource_list : List[Resource]
            A `list` of matching resource from the cache.
        """
        res: List[Resource] = (
            self.session_local()
            .query(Resource)
            .filter(Resource[field].ilike(f"%{query}%"))  # type: ignore
            .all()
        )
        return res

    def get(self, r_name: str) -> Optional[Resource]:
        """Get a resource by `r_name` from the cache if it exists.

        Parameters
        ----------
        r_name : str
            The `r_name` of the file to search.

        Returns
        -------
        resource : Resource | None
            The matching `Resource` object from the cache if it exists.
        """
        return (
            self.session_local()
            .query(Resource)
            .filter(Resource.r_name == r_name)  # type: ignore
            .first()
        )

    def remove(self, r_name: str) -> None:
        """Remove a `Resource` from the cache by `r_name`.

        Parameters
        ----------
        r_name : str
            The `r_name` of the resource to remove.
        """
        session = self.session_local()
        res: Resource = (
            session.query(Resource)
            .filter(Resource.r_name == r_name)  # type: ignore
            .first()
        )
        session.delete(res)  # type: ignore
        session.commit()

        # remove file
        Path(str(res.r_path)).unlink()

    def purge(self):
        """Remove all files from cache."""
        for file in self.cache_dir.iterdir():
            file.unlink()

    def update(
        self, r_name: str, f_path: StrPath, action: str = "copy"
    ) -> Resource:
        """Update a resource in the cache.

        Parameters
        ----------
        r_name : str
            The `r_name` of the resource in cache.
        f_path : str | Path
            The path to the new file to replace the existing one in the cache.
        action : str
            Either `"copy"` or `"move"`. Default = `"copy"`.

        Returns
        -------
        resource : Resource
            The updated cache `Resource` containing the new file.
        """
        if isinstance(f_path, str):
            f_path = Path(f_path)

        if not f_path.exists():
            raise Exception(f"File: '{f_path}' does not exist")

        # get current record
        res = self.get(r_name)

        if res is None:
            _logger.info(
                "File with name '%s' does not exist, adding instead using "
                "default arguments except 'action'.",
                r_name,
            )
            return self.add(r_name, f_path, action=action)

        # copy the file to cache
        self._copy_or_move(action, f_path, str(res.r_path), r_name)

        res.create_time = res.access_time = res.last_modified_time = func.now()

        session = self.session_local()

        session.add(res)  # type: ignore
        session.commit()
        session.refresh(res)  # type: ignore

        return res
