import tempfile
import uuid
from pathlib import Path
from shutil import copy2, move

from typing import Union
import logging
import sys


def create_tmp_dir() -> str:
    """Create a temporary directory.

    Returns:
        str: path to the directory
    """
    return tempfile.mkdtemp()


def generate_id() -> str:
    """Generate uuid.

    Returns:
        str: unique string for use as id
    """
    return uuid.uuid4().hex


def copy_or_move(
    source: Union[str, Path], target: Union[str, Path], rname: str, action: str = "copy"
) -> None:
    """Copy or move a resource from `source` to `target`

    Args:
        source (Union[str, Path]): source location of the resource to copy of move.
        target (Union[str, Path]): destination to copy of move to.
        rname (str): Name of resource to add to cache
        action (str): copy of move file from source. Defaults to copy.

    Raises:
        ValueError: if action is not `copy` or `move`.
        Exception: Error storing resource in the cache directory.
    """

    if action not in ["copy", "move"]:
        raise ValueError(f"Action must be either 'move' or 'copy', provided {action}")

    try:
        if action == "copy":
            copy2(source, target)
        elif action == "move":
            move(str(source), target)
    except Exception as e:
        raise Exception(
            f"Error storing resource: '{rname}' from: '{source}' in '{target}'",
        ) from e


def setup_logging(loglevel):
    """Setup basic logging.

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )
