# Source Cache Output Plan

Future source-cache record kinds:

- pypi_project_metadata_summary
- pypi_release_metadata_summary
- pypi_file_metadata_summary
- pypi_requires_python_summary
- pypi_classifier_summary
- pypi_yanked_status_summary
- pypi_dependency_metadata_summary

Required future constraints:

- metadata summaries only
- no wheel downloads
- no sdist downloads
- no package file downloads
- no package archive inspection
- no package installation
- no dependency resolution
- no raw payload dumps
- no executable payloads
- no private package/index access
- no private data
- source attribution
- package identity review status
- dependency metadata caution status
- freshness/invalidation policy
- source policy ref
- rate-limit/response metadata summary only
