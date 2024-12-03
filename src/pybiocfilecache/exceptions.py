__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class BiocCacheError(Exception):
    """Base exception for BiocFileCache errors."""


class NoFpathError(BiocCacheError):
    """Source file does not exist."""


class RnameExistsError(BiocCacheError):
    """Resource name already exists in cache."""


class RpathTimeoutError(BiocCacheError):
    """Resource path does not exist after timeout."""


class CacheSizeLimitError(BiocCacheError):
    """Cache size limit would be exceeded."""


class ResourceValidationError(BiocCacheError):
    """Resource failed validation check."""


class InvalidRnameError(BiocCacheError):
    """Invalid resource name format."""
