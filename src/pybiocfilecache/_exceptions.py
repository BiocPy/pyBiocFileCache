__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


class NoFpathError(Exception):
    """An error for when the source file does not exist."""


class RnameExistsError(Exception):
    """An error for when the key already exists in the cache."""


class RpathTimeoutError(Exception):
    """An error for when the 'rpath' does not exist after a timeout."""
