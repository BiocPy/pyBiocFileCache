# pyBiocFileCache

An attempt at implementing a Python version of 
the [BiocFileCache R package](https://github.com/Bioconductor/BiocFileCache)

Can be used as a cache interface for any file based system

***Note: Package is in development. Use with caution!!***

## Description

## Installation

PyPI - https://pypi.org/project/pyBiocFileCache/

```shell
pip install pyBiocFileCache
```

## Create a cache directory 

```python
from pybiocfilecache import BiocFileCache
import os

bfc = BiocFileCache(cache_dir = "path/to/cache/dir")
```

Once the cache directory is created, the the `BiocFileCache` class object
allows you to:
- Add a resource with the `add` method
- Get a resource from cache with the `get` method
- Update a resource with the `update` method
- Remove a resource with the `remove` method
- Purge the entire cache with the `purge` method

### Add a resource to cache
```python
res = bfc.add("test1", "path/to/resource.txt")
print(res)
```

### Get resource from cache
```python
res = bfc.get("test1")
print(res)
```

### Remove resource from cache
```python
res = bfc.remove("test1")
print(res)
```

### Update resource in cache
```python
res = bfc.update("test1")
print(res)
```

### purge the cache
```python
bfc.purge()
```


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
