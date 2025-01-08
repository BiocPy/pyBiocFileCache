import hashlib
import logging
import re
import tempfile
import urllib.request
import uuid
import zlib
from pathlib import Path
from shutil import copy2, move
from typing import Literal

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"

logger = logging.getLogger(__name__)


def create_tmp_dir() -> Path:
    """Create a temporary directory."""
    return Path(tempfile.mkdtemp())


def generate_uuid() -> str:
    """Generate unique identifier."""
    return uuid.uuid4().hex


def generate_id(size) -> str:
    """Generate unique identifier."""
    size += 1
    return "BFC" + str(size)


def validate_rname(rname: str, pattern: str) -> bool:
    """Validate resource name format."""
    return bool(re.match(pattern, rname))


def calculate_file_hash(path: Path, algorithm: str = "md5") -> str:
    """Calculate file checksum."""
    hasher = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_file_size(path: Path) -> int:
    """Get file size in bytes."""
    return path.stat().st_size


def compress_file(source: Path, target: Path) -> None:
    """Compress file using zlib."""
    with open(source, "rb") as sf, open(target, "wb") as tf:
        tf.write(zlib.compress(sf.read()))


def decompress_file(source: Path, target: Path) -> None:
    """Decompress file using zlib."""
    with open(source, "rb") as sf, open(target, "wb") as tf:
        tf.write(zlib.decompress(sf.read()))


def copy_or_move(
    source: Path, target: Path, rname: str, action: Literal["copy", "move", "asis"] = "copy", compress: bool = False
) -> None:
    """Copy or move a resource."""
    if action not in ["copy", "move", "asis"]:
        raise ValueError(f"Invalid action: {action}")

    try:
        if action == "copy":
            if compress:
                compress_file(source, target)
            else:
                copy2(source, target)
        elif action == "move":
            if compress:
                compress_file(source, target)
                source.unlink()
            else:
                move(str(source), target)
        elif action == "asis":
            pass
    except Exception as e:
        raise Exception(f"Failed to store resource '{rname}' from '{source}' to '{target}'") from e


def download_web_file(url: str, filename: str, download: bool):
    tmp_dir = create_tmp_dir()

    outpath = tmp_dir / filename

    if download:
        urllib.request.urlretrieve(url, filename=outpath)
    else:
        open(outpath, "a").close()
