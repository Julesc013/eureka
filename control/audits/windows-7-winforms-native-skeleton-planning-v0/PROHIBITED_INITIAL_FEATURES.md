# Prohibited Initial Features

The future initial skeleton must not include:

- downloads
- installers
- install handoff
- package-manager integration
- executable launching
- restore, rollback, uninstall, or system mutation
- local cache runtime
- private cache
- private file ingestion
- local archive scanning
- telemetry
- analytics
- accounts
- cloud sync
- diagnostics or crash-report upload
- relay runtime
- local HTTP listener
- FTP, SMB, WebDAV, NFS, Gopher, or protocol bridge behavior
- live backend dependency
- live source probes
- Internet Archive, Google, GitHub, package registry, or external API calls
- URL fetching
- scraping or crawling
- Rust FFI
- Rust runtime replacement
- Python runtime embedding
- production readiness claims
- executable safety claims
- rights clearance claims
- private path exposure in public reports

Any future implementation prompt must restate these prohibitions and validate
that project files do not introduce them.

