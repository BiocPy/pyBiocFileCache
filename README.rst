===========
pyBiocCache
===========


    An attempt at the Python Interface and Implementation of 
    the `BiocFileCache R pacakge<https://github.com/Bioconductor/BiocFileCache>`

    Note: Package is in development. Use with caution!!


Examples:

1. Create a cache directory 

.. code-block:: Python
    
from pyBiocCache import BiocFileCache
import os

bfc = BiocFileCache(cache_dir = os.getcwd() + "/cache")

Once the cache is created, user has a few options to either
    - Create a resource - `add`
    - Get a resource from cache = `get`
    - Remove a resource - `remove`
    - update a resource - `update`
    - purge the entire cache = `purge`

2. Add resource to cache

.. code-block:: Python

rec = bfc.add("test1", os.getcwd() + "/test1.txt")
print(rec)

3. Get resource from cache

.. code-block:: Python

rec = bfc.get("test1")
print(rec)

4. Remove resource from cache

.. code-block:: Python

rec = bfc.remove("test1")
print(rec)

5. Update resource in cache

.. code-block:: Python

rec = bfc.get("test1"m os.getcwd() + "test2.txt")
print(rec)

6. purge the cache

.. code-block:: Python

bfc.purge()

.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
