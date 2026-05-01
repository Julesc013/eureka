# Absence And Gap Contract

Canonical schema: `contracts/api/absence_report.v0.json`.

Absence reports distinguish `no_verified_result`, `known_unresolved_need`,
`source_gap`, `capability_gap`, `policy_gap`, and `unknown`.

This remains contract-only for durable query intelligence. A local no-result
response may explain bounded absence, but it must not imply global absence.
