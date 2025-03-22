[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/pyBiocFileCache.svg)](https://pypi.org/project/pyBiocFileCache/)
![Unit tests](https://github.com/BiocPy/pyBiocFileCache/actions/workflows/run-tests.yml/badge.svg)

# pyBiocFileCache

`pyBiocFileCache` is a Python package that provides a robust file caching system with resource validation, cache size management, file compression, and resource tagging. Compatible with [BiocFileCache R package](https://github.com/Bioconductor/BiocFileCache).

## Installation

Install from [PyPI](https://pypi.org/project/pyBiocFileCache/),

```bash
pip install pybiocfilecache
```

## Quick Start

```python
from pybiocfilecache import BiocFileCache

# Initialize cache
cache = BiocFileCache("path/to/cache/directory")

# Add a file to cache
resource = cache.add("myfile", "path/to/file.txt")

# Retrieve a file from cache
resource = cache.get("myfile")

# Use the cached file
print(resource["rpath"])  # Path to cached file
```

## Advanced Usage

### Configuration

```python
from pybiocfilecache import BiocFileCache, CacheConfig
from datetime import timedelta
from pathlib import Path

# Create custom configuration
config = CacheConfig(
    cache_dir=Path("cache_directory"),
    cleanup_interval=timedelta(days=7),
)

# Initialize cache with configuration
cache = BiocFileCache(config=config)
```

### Resource Management

```python
# Add file with tags and expiration
from datetime import datetime, timedelta

resource = cache.add(
    "myfile",
    "path/to/file.txt",
    tags=["data", "raw"],
    expires=datetime.now() + timedelta(days=30)
)

# List resources by tag
resources = cache.list_resources(tag="data")

# Search resources
results = cache.search("myfile", field="rname")

# Update resource
cache.update("myfile", "path/to/new_file.txt")

# Remove resource
cache.remove("myfile")
```

### Cache Statistics and Maintenance

```python
# Get cache statistics
stats = cache.get_stats()
print(stats)

# Clean up expired resources
removed_count = cache.cleanup()

# Purge entire cache
cache.purge()
```
