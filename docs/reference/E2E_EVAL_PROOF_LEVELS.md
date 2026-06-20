# E2E Eval Proof Levels

The autonomous E2E evaluation oracle uses deterministic proof levels. A proof
level states what a case proves and what it does not prove.

## shape_proof

Proves packet shape, required fields, stable identifiers, and parseability.

Does not prove semantic correctness, authority, usefulness, or recovery.

## semantic_proof

Proves intended status, constraint preservation, expected result lane,
why-matched or uncertainty behavior, and metamorphic relations.

Does not automatically prove truth authority or mutation safety.

## authority_proof

Proves no forbidden authority transition, no unauthorized store write,
synthetic/preview/reviewed distinctions, public/private boundary posture, and
network/provider posture.

## recovery_proof

Proves replay, rollback, restart, partial failure behavior, corruption
rejection, and prior state preservation.

## parity_proof

Proves semantic facts remain equivalent across representations. It does not
require byte-identical JSON, text, HTML, and snapshot output.

## operational_profile

Measures local latency, traced Python allocation, generated output bytes, file
count, and case duration.

This is not production capacity proof and is not a production-readiness claim.

## Criticality

Critical cases cover authority boundaries, privacy, unauthorized writes,
network/provider isolation, truth leakage, rollback integrity, and replay
integrity. Any critical failure fails the suite.

Required cases cover known-answer semantics, metamorphic behavior, constraints,
duplicates/conflicts, recovery, and parity. Any required failure fails the
suite unless it is explicitly recorded as a named capability gap.

Advisory cases cover resource and diagnostic profiles. Advisory failures yield
`PASS_WITH_WARNINGS` unless a hard safety cap is exceeded.

No weighted score may hide a critical or required failure.
