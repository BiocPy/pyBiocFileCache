from pybioccache.BiocFileCache import BiocFileCache
import os

bfc = BiocFileCache(os.getcwd() + "/cache")

print(bfc)

bfc.add("test1", os.getcwd() + "/src/pybioccache/db/__init__.py")