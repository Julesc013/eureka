# AIDE Task Queue

This directory contains repo-operating task queues for Eureka. It does not
define product runtime behavior and it does not imply a local AIDE product CLI
exists in this repository.

Files:

- `queue.yaml`: JSON-subset YAML list of near-term repo tasks.
- `audit_backlog.yaml`: JSON-subset YAML backlog items derived from repo
  audits.

Future agents may update these files when a prompt explicitly asks for queue or
audit-backlog maintenance. They should keep entries evidence-backed and should
not mark speculative product behavior as implemented.

