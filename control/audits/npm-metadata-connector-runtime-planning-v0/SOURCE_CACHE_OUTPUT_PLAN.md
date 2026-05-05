# Source Cache Output Plan

Future source-cache record kinds:

- `npm_package_metadata_summary`
- `npm_version_metadata_summary`
- `npm_dist_tag_metadata_summary`
- `npm_tarball_metadata_summary`
- `npm_engines_metadata_summary`
- `npm_license_metadata_summary`
- `npm_dependency_metadata_summary`
- `npm_lifecycle_script_metadata_summary`
- `npm_deprecation_status_summary`
- `npm_publisher_maintainer_metadata_summary`

Required constraints: metadata summaries only, no tarball downloads, no package file downloads, no package archive inspection, no package installation, no dependency resolution, no lifecycle script execution, no npm audit, no raw payload dumps, no executable payloads, no private package/registry access, no private data, source attribution, package identity review status, scoped package review status, dependency metadata caution status, lifecycle-script risk status, freshness/invalidation policy, source policy ref, and rate-limit/response metadata summary only.
