import os
import shutil

from datetime import timedelta
from pybiocfilecache import BiocFileCache, CacheConfig
from pathlib import Path
import pytest
import tempfile

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

CACHE_DIR = tempfile.mkdtemp() + "/cache"


def test_create_cache():
    bfc = BiocFileCache(CACHE_DIR)
    assert os.path.exists(CACHE_DIR)

    bfc.check_metadata_key("schema_version")

    bfc.purge()


def test_add_get_list_operations():
    bfc = BiocFileCache(CACHE_DIR)

    rtrip = bfc.add("test1", os.getcwd() + "/tests/data/test1.txt")
    rec1 = bfc.get("test1")
    assert rec1 is not None

    bfc.add("test2", os.getcwd() + "/tests/data/test2.txt")
    rec2 = bfc.get("test2")
    assert rec2 is not None

    frec1 = open(rec1["rpath"], "r").read().strip()
    assert frec1 == "test1"

    frec2 = open(rec2["rpath"], "r").read().strip()
    assert frec2 == "test2"

    shutil.copy(os.getcwd() + "/tests/data/test2.txt", os.getcwd() + "/tests/data/test3.txt")
    bfc.add("test3_asis", os.getcwd() + "/tests/data/test3.txt", action="asis")
    rec3 = bfc.get("test3_asis")
    assert rec3 is not None
    assert rec3["rpath"] == os.getcwd() + "/tests/data/test3.txt"

    frec3 = open(rec3["rpath"], "r").read().strip()
    assert frec3 == "test2"

    rtrip = bfc.list_resources()
    assert len(rtrip) == 3

    downurl = "https://bioconductor.org/packages/stats/bioc/BiocFileCache/BiocFileCache_2024_stats.tab"
    add_url = bfc.add(rname="download_link", fpath=downurl, rtype="web")

    row = bfc.get(rid=add_url["rid"])
    assert row["fpath"] == downurl

    rtrip = bfc.list_resources()
    assert len(rtrip) == 4

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

def test_meta_operations():
    bfc = BiocFileCache(CACHE_DIR)

    bfc.add("test1", os.getcwd() + "/tests/data/test1.txt")
    rec1 = bfc.get("test1")
    assert rec1 is not None

    with pytest.raises(Exception):
        bfc.add_metadata("schema_version", "something")

    bfc.check_metadata_key("schema_version")

    bfc.add_metadata("language", "python")

    downurl = "https://bioconductor.org/packages/stats/bioc/BiocFileCache/BiocFileCache_2024_stats.tab"
    add_url = bfc.add(rname="download_link", fpath=downurl, rtype="web")

    rec = bfc.get_metadata("schema_version")
    assert rec["value"] == "0.99.4"

    rec = bfc.get_metadata("language")
    assert rec["value"] == "python"

    rtrip = bfc.list_resources()
    assert len(rtrip) == 2

    bfc.purge()

def test_cache_with_config():
    # Create custom configuration
    config = CacheConfig(
        cache_dir=Path(CACHE_DIR),
        cleanup_interval=timedelta(days=7),
    )

    bfc = BiocFileCache(config=config)

    bfc.check_metadata_key("schema_version")

    bfc.add("test1", os.getcwd() + "/tests/data/test1.txt")
    rec1 = bfc.get("test1")
    assert rec1 is not None

    rtrip = bfc.list_resources()
    assert len(rtrip) == 1

    bfc.update("test1", os.getcwd() + "/tests/data/test2.txt")
    rec1 = bfc.get("test1")
    assert rec1 is not None

    rtrip = bfc.list_resources()
    assert len(rtrip) == 1

    bfc.cleanup()

    bfc.purge()
