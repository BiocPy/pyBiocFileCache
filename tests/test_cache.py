import os

from pybiocfilecache.BiocFileCache import BiocFileCache

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

CACHE_DIR = os.getcwd() + "/cache"

def test_create_cache():
    assert os.path.exists(CACHE_DIR) == False
    bfc = BiocFileCache(CACHE_DIR)
    assert os.path.exists(CACHE_DIR == True)

    bfc.purge()

def test_add_get_operations():
    # try:
    #     shutil.rmtree(cache_dir)
    # except OSError as e:
    #     print("Error: %s : %s" % (cache_dir, e.strerror))
    #     assert False

    bfc = BiocFileCache(CACHE_DIR)

    bfc.add("test1", os.getcwd() + "/tests/data/test1.txt")
    rec1 = bfc.get("test1")
    assert rec1 != None

    bfc.add("test2", os.getcwd() + "/tests/data/test2.txt")
    rec2 = bfc.get("test2")
    assert rec2 != None

    frec1 = open(rec1.rpath, "r").read()
    assert frec1 == "test1"

    frec2 = open(rec2.rpath, "r").read()
    assert frec2 == "test2"

    bfc.purge()

def test_remove_operations():
    # try:
    #     shutil.rmtree(cache_dir)
    # except OSError as e:
    #     print("Error: %s : %s" % (cache_dir, e.strerror))
    #     assert False

    bfc = BiocFileCache(CACHE_DIR)

    bfc.add("test1", os.getcwd() + "/tests/data/test1.txt")
    rec1 = bfc.get("test1")
    assert rec1 != None

    bfc.add("test2", os.getcwd() + "/tests/data/test2.txt")
    rec2 = bfc.get("test2")
    assert rec2 != None

    bfc.remove("test1")
    rec1 = bfc.get("test1")
    assert rec1 == None

    bfc.purge()