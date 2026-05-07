# ADR: Eureka Track Execution Order

- Status: accepted
- Date: 2026-05-07

## Decision

Future Eureka work proceeds in this order:

1. A0 - convergence / preflight
2. Track A - representation and view-model spine
3. Manual Observation Batch 0
4. Track B - Eureka Node, work units, candidates, source/evidence/review loop
5. Track D - snapshot and relay substrate
6. Track C - native clients
7. Track E - hosting and operations

The next task is `TRACK-A-01 - Host/profile/representation contract bundle`.

## Rationale

Track A must come first because product-facing surfaces need a shared
representation, host-profile, compatibility, evidence, and action vocabulary
before implementation widens.

Manual Observation Batch 0 remains human-operated and should not be fabricated
or automated by Codex.

Track B follows because candidates, sources, evidence, work units, and review
loops need the Track A view-model spine before they can safely feed public or
master-index-oriented work.

Track D comes before Track C because native clients need stable snapshot and
relay substrate before any native project creation.

Track E remains last because hosted public alpha multiplies claim risk and
requires operator evidence for hosting, backend URL, DNS/TLS, abuse controls,
rate limits, monitoring, rollback, and disabled live probes.

## Consequences

- Old P-number prompts are not run blindly.
- Early public-alpha-shaped work is interpreted as local, staged, static, or
  localhost rehearsal evidence.
- Actual hosted public alpha is Track E only.
- No native project is created before Track C.
- No product behavior changes under AIDE-only or convergence tasks.
