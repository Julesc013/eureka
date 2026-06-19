# AIDE Track Authority Improvements

This backlog was recorded during `E2E-REFERENCE-SYSTEM-TRACK-00`.

## Current Capabilities Used

AIDE currently provides useful guardrails for:

- task packets
- protected path declarations
- queue integrity
- changed-test selection
- doctor and validate checks
- commit checks
- external validation handoffs
- artifact ingest
- branch and promotion checks
- generated-output cleanliness

## Current Limitations

The E2E track exposed these limits:

- no native inherited track authority
- explicit child packets are needed for each task
- packets can become oversized
- accepted long-lived branches still trigger task-ID branch-name warnings
- exact task-state coupling can drift as strategies change
- generated artifact retention can create noise
- external run IDs are still operator-managed

## Improvement Backlog

Later AIDE work should consider:

- native track inheritance
- capability-based successor semantics
- smaller generated task packets
- automatic packet compaction
- accepted branch profiles
- unique run-ID generation
- compact external-result ingest
- failure-family clustering
- generated-artifact retention policies
- dependency-aware test selection
- promotion gates based on evidence and capabilities instead of exact queue text

These are AIDE improvements, not product semantics. Any AIDE implementation
change should be authorized separately.

