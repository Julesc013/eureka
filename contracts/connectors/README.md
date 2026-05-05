# Connector Contracts

Connector contracts define approval, manifest, and policy records for future bounded source connectors. They are not connector runtime, source sync execution, public-query fanout, source cache mutation, evidence ledger mutation, candidate mutation, or master-index mutation.

## P72 Wayback/CDX/Memento Connector Approval Pack v0

Completed as an approval-only contract pack. It adds no Wayback/CDX/Memento connector runtime, no external calls, no archived content fetch, no capture replay, no WARC download, no public-query fanout, no telemetry, no credentials, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P73 GitHub Releases Connector Approval Pack v0.

<!-- P73-GITHUB-RELEASES-SUMMARY-START -->
## P73 GitHub Releases Connector Approval Pack v0

Completed as an approval-only release metadata connector pack. It adds no live GitHub connector runtime, no external calls, no GitHub API calls, no repository clone, no release fetch, no release asset download, no source archive download, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P74 PyPI Metadata Connector Approval Pack v0.
<!-- P73-GITHUB-RELEASES-SUMMARY-END -->

<!-- P74-PYPI-METADATA-SUMMARY-START -->
## P74 PyPI Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live PyPI connector runtime, no external calls, no PyPI API calls, no package metadata fetch, no release fetch, no wheel download, no sdist download, no package file download, no package install, no dependency resolution, no package archive inspection, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P75 npm Metadata Connector Approval Pack v0.
<!-- P74-PYPI-METADATA-SUMMARY-END -->

<!-- P75-NPM-METADATA-SUMMARY-START -->
## P75 npm Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live npm connector runtime, no external calls, no npm registry API calls, no npm/yarn/pnpm CLI calls, no package metadata fetch, no version fetch, no dist-tag fetch, no tarball metadata fetch, no tarball download, no package file download, no package install, no dependency resolution, no package archive inspection, no lifecycle script execution, no npm audit, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires package identity review, scoped package review, dependency metadata caution, lifecycle script risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P76 Software Heritage Connector Approval Pack v0.
<!-- P75-NPM-METADATA-SUMMARY-END -->

<!-- P76-SOFTWARE-HERITAGE-SUMMARY-START -->
## P76 Software Heritage Connector Approval Pack v0

Completed as an approval-only software identity/archive metadata connector pack. It adds no live Software Heritage connector runtime, no external calls, no Software Heritage API calls, no SWHID resolution, no origin/visit/snapshot/release/revision/directory/content lookup, no source code download, no repository clone, no source archive download, no source file retrieval, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires SWHID/origin/repository identity review, source-code-content risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P77 Public Hosted Deployment Evidence v0.
<!-- P76-SOFTWARE-HERITAGE-SUMMARY-END -->
