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
