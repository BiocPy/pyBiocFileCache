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

        max_size_bytes:
            Maximum total size of cache.
            None for unlimited.

        cleanup_interval:
            How often to run expired resource cleanup.
            None for no cleanup.

        rname_pattern:
            Regex pattern for valid resource names.

        hash_algorithm:
            Algorithm to use for file checksums.

        compression:
            Whether to compress cached files.
    """

    cache_dir: Path
    max_size_bytes: Optional[int] = None
    cleanup_interval: Optional[timedelta] = None  # timedelta(days=30)
    rname_pattern: str = r"^[a-zA-Z0-9_-]+$"
    hash_algorithm: str = "md5"
    compression: bool = False
