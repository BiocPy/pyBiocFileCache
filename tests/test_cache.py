import os

from pybiocfilecache.BiocFileCache import BiocFileCache

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

CACHE_DIR = os.getcwd() + "/cache"


def test_create_cache():
    bfc = BiocFileCache(CACHE_DIR)
    assert os.path.exists(CACHE_DIR)

    bfc.purge()


def test_add_get_operations():
    bfc = BiocFileCache(CACHE_DIR)

    bfc.add("test1", os.getcwd() + "/tests/data/test1.txt")
    rec1 = bfc.get("test1")
    assert rec1 is not None

    bfc.add("test2", os.getcwd() + "/tests/data/test2.txt")
    rec2 = bfc.get("test2")
    assert rec2 is not None

    frec1 = open(rec1.rpath, "r").read().strip()
    assert frec1 == "test1"

    frec2 = open(rec2.rpath, "r").read().strip()
    assert frec2 == "test2"

    bfc.add("test3_asis", os.getcwd() + "/tests/data/test2.txt", action="asis")
    rec3 = bfc.get("test3_asis")
    assert rec3 is not None
    assert rec3.rpath == os.getcwd() + "/tests/data/test2.txt"

    frec3 = open(rec3.rpath, "r").read().strip()
    assert frec3 == "test2"

    bfc.purge()


def test_remove_operations():
    bfc = BiocFileCache(CACHE_DIR)

    bfc.add("test1", os.getcwd() + "/tests/data/test1.txt")
    rec1 = bfc.get("test1")
    assert rec1 is not None

    bfc.add("test2", os.getcwd() + "/tests/data/test2.txt")
    rec2 = bfc.get("test2")
    assert rec2 is not None

    bfc.remove("test1")
    rec1 = bfc.get("test1")
    assert rec1 is None

    bfc.purge()
