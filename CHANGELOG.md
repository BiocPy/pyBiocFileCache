# Changelog

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
