# Changelog

## Version 0.6.1 - 0.6.2

- Generate rid's that match with R's cache.
- Remove rname pattern checks.
- Add functions to access metadata table.
- Add function to add web urls and download them if needed.
- Rename GitHub actions for consistency with the rest of the packages.

## Version 0.6.0

- Reverting schema changes that break compatibility with the R/BiocFileCache implementation.
- Added support for Python 3.13

## Version 0.5.5

- chore: Remove Python 3.8 (EOL).
- precommit: Replace docformatter with ruff's formatter.

## Version 0.5.0

- SQLAlchemy session management
  * Implemented proper session handling
  * Fixed `DetachedInstanceError` issues and added helper method `_get_detached_resource` for consistent session management
  * Improved transaction handling with commits and rollbacks

- New features
  * Added cache statistics with `get_stats()` method
  * Implemented resource tagging
  * Added cache size management
  * Added support for file compression
  * Added resource validation with checksums
  * Improved search
  * Added metadata export/import functionality

## Version 0.4.1

- Method to list all resources.

## Version 0.4

- Migrate the schema to match R/Bioconductor's BiocFileCache (Check out [this issue](https://github.com/BiocPy/pyBiocFileCache/issues/11)). Thanks to [@khoroshevskyi ](https://github.com/khoroshevskyi) for the PR.

## Version 0.1

- Initial release of the package, Setting up all the actions.
