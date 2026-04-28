# AIDE Reports

This directory is reserved for repo-operating reports. It does not contain
product runtime state and should not be treated as a source of product truth.

Audit reports that belong under version control should usually live in
`control/audits/` with structured findings. Temporary local run output should
stay outside the repo unless a prompt explicitly asks for a committed evidence
artifact.

Search Usefulness Backlog Triage v0 records its governed backlog under
`control/backlog/search_usefulness_triage/`. If an operator later captures a
triage review report, keep it as evidence here and leave runtime behavior in
the product layers.

Search Usefulness Audit Delta v0 records its committed audit/reporting pack
under `control/audits/search-usefulness-delta-v0/`. It is the canonical place
for the current usefulness-delta summary; do not duplicate volatile local audit
run dumps here.

Search Usefulness Audit Delta v1 records the post-source-expansion delta under
`control/audits/search-usefulness-delta-v1/`. It is also reporting-only and
does not belong in runtime state.

Hard Eval Satisfaction Pack v0 records the archive-resolution hard-eval
satisfaction pass under `control/audits/hard-eval-satisfaction-v0/`. It is
source-backed eval evidence, not AIDE runtime state.

Old-Platform Result Refinement Pack v0 records the archive-resolution
result-shape refinement pass under
`control/audits/old-platform-result-refinement-v0/`. It is deterministic eval
evidence, not AIDE runtime state.

Generated Public Data Summaries v0 records committed static machine-readable
summaries under `public_site/data/` and generated validation copies under
`site/dist/data/`. No separate AIDE runtime report is needed; those JSON files
are publication artifacts, not AIDE product state.

Lite/Text/Files Seed Surfaces v0 records committed static compatibility
surfaces under `public_site/lite/`, `public_site/text/`, and
`public_site/files/`, with generated validation copies under `site/dist/`.
No separate AIDE runtime report is needed; those files are publication
artifacts and do not add live search, downloads, snapshots, relay behavior, or
native-client runtime.

Static Resolver Demo Snapshots v0 records committed static resolver examples
under `public_site/demo/`, with generated validation copies under
`site/dist/demo/`. No separate AIDE runtime report is needed; those files are
publication artifacts and do not add live search, live API semantics, backend
hosting, external observations, or production behavior.

Custom Domain / Alternate Host Readiness v0 records readiness inventories under
`control/inventory/publication/` and operations/reference docs under `docs/`.
No separate AIDE runtime report is needed; this is host-portability governance
only and does not add DNS records, `CNAME`, provider config, alternate-host
deployment, backend hosting, live probes, or production behavior.

Live Backend Handoff Contract v0 records future `/api/v1` handoff inventories
under `control/inventory/publication/` and architecture/reference docs under
`docs/`. No separate AIDE runtime report is needed; this is contract-only
publication governance and does not host a backend, make `/api/v1` live, enable
live probes, implement CORS/auth/rate limits, or create production API
guarantees.
