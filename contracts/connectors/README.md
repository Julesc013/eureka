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
