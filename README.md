# pyBiocFileCache

An attempt at implementing a Python version of 
the [BiocFileCache R package](https://github.com/Bioconductor/BiocFileCache)

***Note: Package is in development. Use with caution!!***




## Description

### Installation

***Note: Package is not on PyPI yet.***

```
pip install git+https://github.com/epiviz/pyBiocFileCache
```

#### Create a cache directory 

```
from pybiocfilecache import BiocFileCache
import os

bfc = BiocFileCache(cache_dir = os.getcwd() + "/cache")
```

Once the cache directory is created, the library allows
- Create a resource - `add`
- Get a resource from cache - `get`
- Remove a resource - `remove`
- update a resource - `update`
- purge the entire cache - `purge`

#### Add a resource to cache

(for testing use the temp files in the `tests/data` directory)

```
rec = bfc.add("test1", os.getcwd() + "/test1.txt")
print(rec)
```

#### Get resource from cache

```
rec = bfc.get("test1")
print(rec)
```

#### Remove resource from cache

```
rec = bfc.remove("test1")
print(rec)
```

#### Update resource in cache

```
rec = bfc.get("test1"m os.getcwd() + "test2.txt")
print(rec)
```

#### purge the cache

```
bfc.purge()
```


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
