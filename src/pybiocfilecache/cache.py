import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from time import sleep, time
from typing import Any, Dict, Iterator, List, Literal, Optional, Tuple, Union

from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from .config import CacheConfig
from .const import SCHEMA_VERSION
from .models import Base, Metadata, Resource
from .utils import (
    calculate_file_hash,
    copy_or_move,
    create_tmp_dir,
    download_web_file,
    generate_id,
    generate_uuid,
    validate_rname,
)

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"

logger = logging.getLogger(__name__)


class BiocFileCache:
    """Enhanced file caching module.

    Features:
    - Resource validation and integrity checking
    - Cache size management
    - Cleanup of expired resources
    """

    def __init__(self, cache_dir: Optional[Union[str, Path]] = None, config: Optional[CacheConfig] = None):
        """Initialize cache with optional configuration.

        Args:
            cache_dir:
                Path to cache directory.
                Defaults to tmp location, :py:func:`~.utils.create_tmp_dir`.
                Ignored if config already contains the path to the cache directory.

            config:
                Optional configuration.

        """
        if config is None:
            cache_dir = Path(cache_dir) if cache_dir else create_tmp_dir()
            config = CacheConfig(cache_dir=cache_dir)

        self.config = config
        self._setup_cache_dir()
        db_schema_version = self._setup_database()

        if db_schema_version != SCHEMA_VERSION:
            print(db_schema_version)
            raise RuntimeError(f"Database version is not {SCHEMA_VERSION}.")

        self._last_cleanup = datetime.now()

    def _setup_cache_dir(self) -> bool:
        if not self.config.cache_dir.exists():
            self.config.cache_dir.mkdir(parents=True, exist_ok=True)

    def _setup_database(self) -> None:
        db_path = self.config.cache_dir / "BiocFileCache.sqlite"
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            connect_args={"check_same_thread": False},
        )

        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT value FROM metadata
                WHERE key = 'schema_version'
            """)
            )
            row = result.fetchone()

            if row is not None:
                return row[0]

            conn.execute(
                text("""
                INSERT INTO metadata (key, value)
                VALUES ('schema_version', :version);
            """),
                {"version": SCHEMA_VERSION},
            )
            conn.commit()

            return SCHEMA_VERSION

    def _get_detached_resource(self, session: Session, resource: Resource) -> Optional[Resource]:
        """Get a detached copy of a resource."""
        if resource is None:
            return None
        session.refresh(resource)
        session.expunge(resource)
        return resource

    def __enter__(self) -> "BiocFileCache":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Clean up resources."""
        self.engine.dispose()

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """Provide database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _validate_rname(self, rname: str) -> None:
        """Validate resource name format."""
        if not validate_rname(rname, self.config.rname_pattern):
            raise Exception(f"Resource name '{rname}' doesn't match pattern " f"'{self.config.rname_pattern}'")

    def _should_cleanup(self) -> bool:
        """Check if cache cleanup should be performed.

        Returns:
            True if `cleanup_interval` is set and time since last cleanup exceeds it.
        """
        if self.config.cleanup_interval is None:
            return False

        return datetime.now() - self._last_cleanup > self.config.cleanup_interval

    def cleanup(self) -> int:
        """Remove expired resources from the cache.

        Returns:
            Number of resources removed.

        Note:
            - If `cleanup_interval` is None, this method will still run if called explicitly.
            - Only removes resources with non-None expiration dates.
        """
        if not any([self.config.cleanup_interval, self._should_cleanup()]):
            return 0  # Early return if automatic cleanup is disabled

        removed = 0
        with self.get_session() as session:
            # Only query resources that have expiration dates
            expired = (
                session.query(Resource)
                .filter(
                    Resource.expires.isnot(None),  # Only check resources with expiration
                    Resource.expires < datetime.now(),
                )
                .all()
            )

            for resource in expired:
                try:
                    Path(resource.rpath).unlink(missing_ok=True)
                    session.delete(resource)
                    removed += 1
                except Exception as e:
                    logger.error(f"Failed to remove expired resource: {resource.rname}", exc_info=e)

            session.commit()

        self._last_cleanup = datetime.now()
        return removed

    def get(self, rname: str = None, rid: str = None) -> Optional[Resource]:
        """Get resource by name from cache.

        Args:
            rname:
                Name to identify the resource in cache.

            rid:
                Resource id to search by.

        """
        if rname is None and rid is None:
            raise ValueError("either 'rname' or 'rid' must be provided.")

        with self.get_session() as session:
            if rname is not None:
                resource = session.query(Resource).filter(Resource.rname == rname).first()
            elif rid is not None:
                resource = session.query(Resource).filter(Resource.rid == rid).first()

            if resource is not None:
                # Check if path exists with timeout
                start = time()
                timeout = 30
                while not Path(str(resource.rpath)).exists():
                    if time() - start >= timeout:
                        raise TimeoutError(
                            f"For resource: '{rname}' the rpath does not exist " f"after {timeout} seconds."
                        )
                    sleep(0.1)

                # Update access time
                resource.access_time = datetime.now()
                session.commit()
                return self._get_detached_resource(session, resource)

        return None

    def add(
        self,
        rname: str,
        fpath: Union[str, Path],
        rtype: Literal["local", "web", "relative"] = "relative",
        action: Literal["copy", "move", "asis"] = "copy",
        expires: Optional[datetime] = None,
        download: bool = True,
        ext: bool = True,
    ) -> Resource:
        """Add a resource to the cache.

        Args:
            rname:
                Name to identify the resource in cache.

            fpath:
                Path to the source file.

            rtype:
                Type of resource.
                One of ``local``, ``web``, or ``relative``.
                Defaults to ``local``.

            action:
                How to handle the file ("copy", "move", or "asis").
                Defaults to ``copy``.

            download:
                Whether to download the resource.
                Only used if 'rtype' is "web".

            expires:
                Optional expiration datetime.
                If None, resource never expires.

            ext:
                Whether to use filepath extension when storing in cache.
                Defaults to `True`.

        Returns:
            The `Resource` object added to the cache.
        """
        # self._validate_rname(rname)
        fpath = Path(fpath) if rtype != "web" else fpath

        if self.get(rname) is not None:
            raise FileExistsError(f"Resource '{rname}' already exists")

        if rtype == "web":
            outpath = download_web_file(fpath, Path(fpath).name, download)
            action = "copy"
        else:
            outpath = Path(fpath)

        if action == "asis":
            logger.warning("If action='asis', rtype must be 'local'.")
            rtype = "local"

        # Generate paths and check size
        rid = generate_id(size=len(self))
        uuid = generate_uuid()
        rpath = self.config.cache_dir / f"{uuid}_{outpath.name if ext else outpath.stem}" if action != "asis" else fpath

        # Create resource record
        resource = Resource(
            rid=rid,
            rname=rname,
            rpath=str(rpath),
            rtype=rtype,
            fpath=str(fpath),
            expires=expires,
        )

        # Store file and update database
        with self.get_session() as session:
            session.add(resource)
            session.commit()

            try:
                copy_or_move(outpath, rpath, rname, action, False)

                # Calculate and store checksum
                resource.etag = calculate_file_hash(rpath, self.config.hash_algorithm)
                session.commit()
                result = self._get_detached_resource(session, resource)
                return result

            except Exception as e:
                session.delete(resource)
                session.commit()
                raise Exception("Failed to add resource") from e

    def add_batch(self, resources: List[Dict[str, Any]]) -> List[Resource]:
        """Add multiple resources in a single transaction.

        Args:
            resources:
                List of resources to add.
        """
        results = []
        with self.get_session() as session:
            for resource_info in resources:
                try:
                    resource = self.add(**resource_info)
                    results.append(resource)
                except Exception as e:
                    logger.error(f"Failed to add resource: {resource_info.get('rname')}", exc_info=e)
                    session.rollback()
                    raise
        return results

    def update(
        self,
        rname: str,
        fpath: Union[str, Path],
        action: Literal["copy", "move", "asis"] = "copy",
    ) -> Resource:
        """Update an existing resource.

        Args:
            rname:
                Name to identify the resource in cache.

            fpath:
                Path to the new source file.

            action:
                Either ``copy``, ``move`` or ``asis``.
                Defaults to ``copy``.

        Returns:
            Updated `Resource` object.

        """
        fpath = Path(fpath)
        if not fpath.exists():
            raise FileNotFoundError(f"File '{fpath}' does not exist")

        with self.get_session() as session:
            resource = session.query(Resource).filter(Resource.rname == rname).first()

            if resource is None:
                return self.add(rname=rname, fpath=fpath, action=action)

            old_path = Path(resource.rpath)
            try:
                copy_or_move(fpath, old_path, rname, action, False)

                resource.last_modified_time = datetime.now()
                resource.etag = calculate_file_hash(old_path, self.config.hash_algorithm)

                session.commit()
                return self._get_detached_resource(session, resource)

            except Exception as e:
                session.rollback()
                raise Exception("Failed to update resource") from e

    def remove(self, rname: str) -> None:
        """Remove a resource from cache by name.

        Removes both the cached file and its database entry.

        Args:
            rname:
                Name to identify the resource in cache.

        Raises:
            Exception: If resource removal fails
        """
        with self.get_session() as session:
            resource = session.query(Resource).filter(Resource.rname == rname).first()

            if resource is not None:
                try:
                    # Try to remove the file first
                    rpath = Path(resource.rpath)
                    if rpath.exists():
                        rpath.unlink()

                    # Then remove from database
                    session.delete(resource)
                    session.commit()

                except Exception as e:
                    session.rollback()
                    raise Exception(f"Failed to remove resource '{rname}'") from e

    def list_resources(self, rtype: Optional[str] = None, expired: Optional[bool] = None) -> List[Resource]:
        """List resources in the cache with optional filtering.

        Args:

            rtype:
                Filter resources by type.

            expired:
                Filter by expiration status
                    True: only expired resources
                    False: only non-expired resources
                    None: all resources
                Note: Resources with no expiration are always considered non-expired.

        Returns:
            List of Resource objects matching the filters
        """
        with self.get_session() as session:
            query = session.query(Resource)

            if rtype:
                query = query.filter(Resource.rtype == rtype)
            if expired is not None:
                if expired:
                    query = query.filter(
                        Resource.expires.isnot(None),  # Only check resources with expiration
                        Resource.expires < datetime.now(),
                    )
                else:
                    query = query.filter(
                        (Resource.expires.is_(None))  # Never expires
                        | (Resource.expires > datetime.now())  # Not yet expired
                    )

            resources = query.all()
            return [self._get_detached_resource(session, r) for r in resources]

    def validate_resource(self, resource: Resource) -> bool:
        """Validate resource integrity.

        Args:
            resource:
                Resource to validate.

        Returns:
            True if resource is valid, False otherwise.
        """
        if not resource.etag:
            return True  # No validation if no checksum

        try:
            current_hash = calculate_file_hash(Path(resource.rpath), self.config.hash_algorithm)
            return current_hash == resource.etag
        except Exception as e:
            logger.error(f"Failed to validate resource: {resource.rname}", exc_info=e)
            return False

    # def export_metadata(self, path: Path) -> None:
    #     """Export cache metadata to JSON file."""
    #     data = {
    #         "resources": [
    #             {
    #                 "rname": r.rname,
    #                 "rtype": r.rtype,
    #                 "expires": r.expires.isoformat() if r.expires else None,
    #                 "etag": r.etag,
    #             }
    #             for r in self.list_resources()
    #         ],
    #         "export_time": datetime.now().isoformat(),
    #     }

    #     with open(path, "w") as f:
    #         json.dump(data, f, indent=2)

    # def import_metadata(self, path: Path) -> None:
    #     """Import cache metadata from JSON file."""
    #     with open(path) as f:
    #         data = json.load(f)

    #     with self.get_session() as session:
    #         for resource_data in data["resources"]:
    #             resource = self._get(session, resource_data["rname"])
    #             if resource:
    #                 resource.expires = (
    #                     datetime.fromisoformat(resource_data["expires"]) if resource_data["expires"] else None
    #                 )
    #                 session.merge(resource)
    #         session.commit()

    def verify_cache(self) -> Tuple[int, int]:
        """Verify integrity of all cached resources.

        Returns:
            Tuple of (valid_count, invalid_count).
        """
        valid = invalid = 0
        for resource in self.list_resources():
            if self.validate_resource(resource):
                valid += 1
            else:
                invalid += 1
        return valid, invalid

    def search(self, query: str, field: str = "rname", exact: bool = False) -> List[Resource]:
        """Search for resources by field value.

        Args:
            query:
                Search string.

            field:
                Resource field to search ("rname", "rtype", etc.).

            exact:
                Whether to require exact match.

        Returns:
            List of matching resources.
        """
        with self.get_session() as session:
            if exact:
                resources = session.query(Resource).filter(Resource[field] == query).all()
            else:
                resources = session.query(Resource).filter(Resource[field].ilike(f"%{query}%")).all()

            return [self._get_detached_resource(session, r) for r in resources]

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        with self.get_session() as session:
            total = session.query(Resource).count()
            expired = (
                session.query(Resource)
                .filter(
                    Resource.expires.isnot(None),  # Only check resources with expiration
                    Resource.expires < datetime.now(),
                )
                .count()
            )
            types = dict(session.query(Resource.rtype, func.count(Resource.id)).group_by(Resource.rtype).all())

            return {
                "total_resources": total,
                "expired_resources": expired,
                "resource_types": types,
                "last_cleanup": self._last_cleanup.isoformat(),
                "cleanup_enabled": self.config.cleanup_interval is not None,
            }

    def purge(self, force: bool = False) -> bool:
        """Remove all resources from cache and reset database.

        Args:
            force:
                If True, skip validation and remove all files
                even if database operations fail.

        Returns:
            True if purge was successful, False otherwise.

        Raises:
            Exception: If purge fails and force=False.
        """
        try:
            with self.get_session() as session:
                resources = session.query(Resource).all()
                session.query(Resource).delete()

                for resource in resources:
                    try:
                        Path(resource.rpath).unlink(missing_ok=True)
                    except Exception as e:
                        if not force:
                            session.rollback()
                            raise Exception(f"Failed to remove file for resource '{resource.rname}'") from e
                        logger.warning(f"Failed to remove file for resource '{resource.rname}': {e}")

                session.commit()

            if force:
                for file in self.config.cache_dir.iterdir():
                    if file.name != "BiocFileCache.sqlite":
                        try:
                            if file.is_file():
                                file.unlink()
                            elif file.is_dir():
                                file.rmdir()
                        except Exception as e:
                            logger.warning(f"Failed to remove {file}: {e}")

            self._last_cleanup = datetime.now()
            return True

        except Exception as e:
            if not force:
                raise Exception("Failed to purge cache") from e

            logger.error("Database cleanup failed, forcing file removal", exc_info=e)
            for file in self.config.cache_dir.iterdir():
                if file.name != "BiocFileCache.sqlite":
                    try:
                        if file.is_file():
                            file.unlink()
                        elif file.is_dir():
                            file.rmdir()
                    except Exception as file_e:
                        logger.warning(f"Failed to remove {file}: {file_e}")

            return False

    def __len__(self):
        with self.get_session() as session:
            return session.query(Resource).count()

    def check_metadata_key(self, key: str) -> bool:
        """Check if a key exists in the metadata table.

        Args:
            key:
                Key to search.

        Returns:
            True if the key exists, else False.
        """
        with self.get_session() as session:
            return session.query(Metadata).filter(Metadata.key == key).first() is not None

    def add_metadata(self, key: str, value: str):
        """Add a new metadata key"""
        exists = self.check_metadata_key(key=key)

        if exists:
            # add
            meta = Metadata(key=key, value=value)

            # Store file and update database
            with self.get_session() as session:
                session.add(meta)
                session.commit()
        else:
            raise Exception(f"'key'={key} already exists in metadata.")

    def remove_metadata(self, key: str) -> None:
        """Remove a metadata key."""
        with self.get_session() as session:
            meta = session.query(Metadata).filter(Metadata.key == key).first()

            if meta is not None:
                try:
                    session.delete(meta)
                    session.commit()

                except Exception as e:
                    session.rollback()
                    raise Exception(f"Failed to remove key '{key}'") from e
