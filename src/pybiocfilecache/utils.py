from logging import basicConfig
from pathlib import Path
from sys import stdout
from typing import Union

StrPath = Union[Path, str]


def setup_logging(log_level: int):
    """Config basic logging.

    Parameters
    ----------
    log_level : int
        Minimum log level for emitting messages.
    """
    basicConfig(
        level=log_level,
        stream=stdout,
        format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
