[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/pyBiocFileCache.svg)](https://pypi.org/project/pyBiocFileCache/)
![Unit tests](https://github.com/BiocPy/pyBiocFileCache/actions/workflows/pypi-test.yml/badge.svg)

# pyBiocFileCache

File system based cache for resources & metadata. Compatible with [BiocFileCache R package](https://github.com/Bioconductor/BiocFileCache)

***Note: Package is in development. Use with caution!!***

### Installation

Package is published to [PyPI](https://pypi.org/project/pyBiocFileCache/)

```
pip install pybiocfilecache
```

#### Initialize a cache directory

```
from pybiocfilecache import BiocFileCache
import os

bfc = BiocFileCache(cache_dir = os.getcwd() + "/cache")
```

Once the cache directory is created, the library provides methods to
- `add`: Add a resource or artifact to cache
- `get`: Get the resource from cache
- `remove`: Remove a resource from cache
- `update`: update the resource in cache
- `purge`: purge the entire cache, removes all files in the cache directory

### Add a resource to cache

(for testing use the temp files in the `tests/data` directory)

```
rec = bfc.add("test1", os.getcwd() + "/test1.txt")
print(rec)
```

### Get resource from cache

```
rec = bfc.get("test1")
print(rec)
```

### Remove resource from cache

```
rec = bfc.remove("test1")
print(rec)
```

### Update resource in cache

```
rec = bfc.get("test1"m os.getcwd() + "test2.txt")
print(rec)
```

### purge the cache

```
bfc.purge()
```


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
