import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


logger = logging.getLogger(__name__)


class Migration:
    """Base class for migrations."""

    version: str
    description: str

    @staticmethod
    def up(engine: Engine) -> None:
        """Upgrade to this version."""
        raise NotImplementedError

    @staticmethod
    def down(engine: Engine) -> None:
        """Downgrade from this version."""
        raise NotImplementedError


class Migrator:
    """Handles database schema migrations."""

    def __init__(self, engine: Engine):
        from .migrationV0_5_0 import MigrationV0_5_0

        self.engine = engine
        self.migrations = [MigrationV0_5_0]

    def _detect_version_from_structure(self) -> str:
        """Detect schema version by examining table structure."""
        with self.engine.connect() as conn:
            # Check table structure
            columns = conn.execute(
                text("""
                PRAGMA table_info(resource);
            """)
            ).fetchall()
            column_names = {col[1] for col in columns}

            # Check for columns that indicate version
            if "is_compressed" in column_names:
                return "0.5.0"
            elif "tags" in column_names and "size_bytes" in column_names:
                return "0.5.0"
            else:
                return "0.4.1"

    def get_current_version(self) -> Optional[str]:
        """Get current schema version from database.

        Will attempt to detect version if `schema_version` is not in metadata.
        """
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

            detected_version = self._detect_version_from_structure()
            conn.execute(
                text("""
                INSERT INTO metadata (key, value)
                VALUES ('schema_version', :version);
            """),
                {"version": detected_version},
            )

            return detected_version

    def migrate(self, target_version: Optional[str] = None) -> None:
        """Migrate schema to target version.

        Args:
            target_version:
                Version to migrate to.
                If None, migrates to latest version.
        """
        try:
            current = self.get_current_version()
            latest_version = self.migrations[-1].version
            target_version = target_version or latest_version

            if current == target_version:
                logger.info("Already at target version")
                return

            if current == "0.4.1" and target_version == "0.5.0":
                logger.info("Upgrading from 0.4.1 to 0.5.0")
                self.migrations[0].up(self.engine)
            elif current == "0.5.0" and target_version == "0.4.1":
                logger.info("Downgrading from 0.5.0 to 0.4.1")
                self.migrations[0].down(self.engine)
            else:
                raise ValueError(f"Unsupported migration path: {current} -> {target_version}")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise

            # When we have multiple migrations
            # current_idx = next((i for i, m in enumerate(self.migrations) if m.version == current), None)
            # target_idx = next((i for i, m in enumerate(self.migrations) if m.version == target_version), None)

            # if current_idx is None:
            #     raise ValueError(f"Unknown current version: {current}")
            # if target_idx is None:
            #     raise ValueError(f"Unknown target version: {target_version}")

            # if current_idx < target_idx:
            #     # Upgrade
            #     for migration in self.migrations[current_idx : target_idx + 1]:
            #         logger.info(f"Upgrading to {migration.version}")
            #         migration.up(self.engine)
            # elif current_idx > target_idx:
            #     # Downgrade
            #     for migration in reversed(self.migrations[target_idx + 1 : current_idx + 1]):
            #         logger.info(f"Downgrading from {migration.version}")
            #         migration.down(self.engine)

    def __repr__(self) -> str:
        return f"Migrator(current_version={self.get_current_version()})"
