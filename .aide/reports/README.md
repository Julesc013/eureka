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
