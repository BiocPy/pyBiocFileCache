from sqlalchemy import text
from sqlalchemy.engine import Engine

from .migration import Migration

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class MigrationV0_5_0(Migration):
    """Migration from v0.4.1 to 0.5.0."""

    version = "0.5.0"
    description = "Add tags, size_bytes, compression flag, and update indexes"

    @staticmethod
    def up(engine: Engine) -> None:
        """Upgrade from v0.4.1 to v0.5.0."""
        with engine.begin() as conn:
            # Add new columns
            conn.execute(
                text("""
                ALTER TABLE resource 
                ADD COLUMN tags TEXT;
            """)
            )
            conn.execute(
                text("""
                ALTER TABLE resource 
                ADD COLUMN size_bytes INTEGER;
            """)
            )
            # conn.execute(
            #     text("""
            #     ALTER TABLE resource 
            #     ADD COLUMN is_compressed BOOLEAN DEFAULT FALSE;
            # """)
            # )

            # Calculate size_bytes for existing resources
            conn.execute(
                text("""
                UPDATE resource
                SET size_bytes = (
                    SELECT length(readfile(rpath))
                    FROM resource r2
                    WHERE r2.id = resource.id
                )
                WHERE EXISTS (
                    SELECT 1
                    FROM resource r3
                    WHERE r3.id = resource.id
                    AND r3.rpath IS NOT NULL
                );
            """)
            )

            # Add indexes
            conn.execute(
                text("""
                CREATE UNIQUE INDEX IF NOT EXISTS ix_resource_rname 
                ON resource(rname);
            """)
            )
            conn.execute(
                text("""
                CREATE INDEX IF NOT EXISTS ix_resource_rid 
                ON resource(rid);
            """)
            )

            # Update metadata
            conn.execute(
                text("""
                UPDATE metadata 
                SET value = '0.5.0' 
                WHERE key = 'schema_version';
            """)
            )

    @staticmethod
    def down(engine: Engine) -> None:
        """Downgrade from v0.5.0 to 0.4.1."""
        with engine.begin() as conn:
            # Remove indexes
            conn.execute(text("DROP INDEX IF EXISTS ix_resource_rname;"))
            conn.execute(text("DROP INDEX IF EXISTS ix_resource_rid;"))

            # Remove columns
            # conn.execute(text("ALTER TABLE resource DROP COLUMN is_compressed;"))
            conn.execute(text("ALTER TABLE resource DROP COLUMN size_bytes;"))
            conn.execute(text("ALTER TABLE resource DROP COLUMN tags;"))

            # Update metadata
            conn.execute(
                text("""
                UPDATE metadata 
                SET value = '0.4.1' 
                WHERE key = 'schema_version';
            """)
            )
