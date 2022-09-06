"""Python Implementation of BiocFileCache."""

from sys import version_info

# pylint: disable=useless-import-alias
# flake8: noqa
from .BiocFileCache import BiocFileCache as BiocFileCache

if version_info[:2] >= (3, 8):
    from importlib.metadata import (  # type: ignore # pylint: disable=import-error,no-name-in-module # noqa: E501
        PackageNotFoundError,
        version,
    )
else:
    from importlib_metadata import (  # type: ignore
        PackageNotFoundError,
        version,
    )

try:
    __version__ = version(__name__)  # type: ignore
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
