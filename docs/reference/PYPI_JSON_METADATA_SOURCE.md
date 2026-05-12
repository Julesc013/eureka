# PyPI JSON Metadata Source

Source ID: `pypi_json_metadata`

Operation scope: `metadata_only`

Endpoint shape: `https://pypi.org/pypi/{package_name}/json`

Allowed package for R0-09: `sampleproject`

Policy gates:

- live network use defaults off
- live use requires `--live`
- maximum one request per run
- package name must be `sampleproject`
- User-Agent must include contact posture
- package downloads are disabled
- dependency resolution is disabled
- install and execution are disabled
- source sync is disabled

Normalized fields:

- `name`
- `version`
- `summary`
- `project_urls`
- `release_count`
- `metadata_limitations`

The source module may read the PyPI JSON metadata response body. It does not request download URLs, release files, search endpoints, package archives, or dependency metadata beyond the JSON document returned by the approved endpoint.
