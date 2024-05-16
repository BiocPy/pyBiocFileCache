import logging
import sys
import tempfile
import uuid
from pathlib import Path
from shutil import copy2, move
from typing import Literal, Union

__author__ = "Jayaram Kancherla"
__copyright__ = "jkanche"
__license__ = "MIT"


def create_tmp_dir() -> str:
    """Create a temporary directory.

    Returns:
        Temporary path to the directory.
    """
    return tempfile.mkdtemp()


def generate_id() -> str:
    """Generate uuid.

    Returns:
        Unique string for use as id.
    """
    return uuid.uuid4().hex


def copy_or_move(
    source: Union[str, Path],
    target: Union[str, Path],
    rname: str,
    action: Literal["copy", "move", "asis"] = "copy",
) -> None:
    """Copy or move a resource from ``source`` to ``target``.

    Args:
        source:
            Source location of the resource to copy of move.

        target:
            Destination to copy of move to.

        rname:
            Name of resource to add to cache.

        action:
            Copy of move file from source.
            Defaults to copy.

    Raises:
        ValueError:
            If action is not `copy`, `move` or `asis`.

        Exception:
            Error storing resource in the cache directory.
    """

    if action not in ["copy", "move", "asis"]:
        raise ValueError(
            f"Action must be either 'move', 'copy' or 'asis', provided {action}."
        )

    try:
        if action == "copy":
            copy2(source, target)
        elif action == "move":
            move(str(source), target)
        elif action == "asis":
            pass
    except Exception as e:
        raise Exception(
            f"Error storing resource: '{rname}' from: '{source}' in '{target}'.",
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
