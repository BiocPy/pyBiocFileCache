from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Optional

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@dataclass
class CacheConfig:
    """Configuration for BiocFileCache.

    Attributes:
        cache_dir:
            Directory to store cached files.

        cleanup_interval:
            How often to run expired resource cleanup.
            None for no cleanup.

        rname_pattern:
            Regex pattern for valid resource names.

        hash_algorithm:
            Algorithm to use for file checksums.
    """

    cache_dir: Path
    cleanup_interval: Optional[timedelta] = None  # timedelta(days=30)
    rname_pattern: str = r"^[a-zA-Z0-9_-]+$"
    hash_algorithm: str = "md5"
