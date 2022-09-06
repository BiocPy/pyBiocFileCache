"""Test pyBiocFileCache."""

from os import getcwd
from pathlib import Path
from shutil import rmtree

from pybiocfilecache import BiocFileCache

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

DATA_DIR = Path(__file__).parent.joinpath("data")

bfc = BiocFileCache()

# noqa: B101


def test_create_cache():
    """Test that BiocFileCache creates the cache directory."""
    cache_dir = Path(f"{getcwd()}/cache")
    if cache_dir.exists():
        rmtree(cache_dir)

    BiocFileCache(cache_dir)
    assert cache_dir.exists()


def test_add_get_operations():
    """Test BiocFileCache methods that add resources to cache."""
    bfc.add("test1", DATA_DIR.joinpath("test1.txt"))
    res1 = bfc.get("test1")
    assert res1 is not None

    bfc.add("test2", DATA_DIR.joinpath("test2.txt"))
    res2 = bfc.get("test2")
    assert res2 is not None

    assert Path(str(res1.r_path)).read_text(encoding="utf-8") == "test1"

    assert Path(str(res2.r_path)).read_text(encoding="utf-8") == "test2"

    bfc.purge()


def test_remove_operations():
    """Test BiocFileCache methods that remove resources from cache."""
    bfc.add("test1", DATA_DIR.joinpath("test1.txt"))
    bfc.remove("test1")
    assert bfc.get("test1") is None

    bfc.purge()
