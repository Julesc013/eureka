# Runtime Boundary

P90 does not implement PyPI connector runtime.

- No live PyPI calls occur.
- No PyPI API endpoints are called.
- No package metadata, release metadata, or file metadata is fetched.
- No wheels, sdists, package files, or package archives are downloaded.
- No packages are installed.
- No pip commands are invoked.
- No dependency resolution is performed.
- No package archives are inspected.
- No setup.py or build scripts are executed.
- No source-sync jobs execute.
- No source-cache records are written.
- No evidence-ledger records are written.
- No public search route calls PyPI.
- No arbitrary package fetch exists.
- No downloads, mirroring, or file retrieval exist.
- No credentials or PyPI tokens are configured.
- No telemetry is enabled.
- No indexes are mutated.

Existing recorded-fixture package connector code is not changed by P90.
