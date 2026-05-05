# Runtime Boundary

P89 does not implement GitHub Releases connector runtime.

- No live GitHub calls occur.
- No GitHub API endpoints are called.
- No releases, tags, repository metadata, assets, source archives, raw files, or blobs are fetched.
- No repositories are cloned.
- No source-sync jobs execute.
- No source-cache records are written.
- No evidence-ledger records are written.
- No public search route calls GitHub.
- No arbitrary repository fetch exists.
- No downloads, mirroring, or file retrieval exist.
- No credentials or GitHub tokens are configured.
- No telemetry is enabled.
- No indexes are mutated.

Existing recorded-fixture connector code is not changed by P89.
