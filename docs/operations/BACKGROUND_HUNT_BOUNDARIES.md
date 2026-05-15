# Background Hunt Boundaries

HUNT-07 permits:

- planning hunt-linked WorkUnits,
- running safe deterministic local workers,
- recording worker results and audit refs,
- recording background hunt run history,
- updating WorkUnit transition history.

HUNT-07 forbids:

- source probes,
- extraction,
- model/provider calls,
- agent research workers,
- acquisition or launch actions,
- source sync,
- LAN worker mutation,
- deployment,
- review decision mutation,
- master index mutation,
- production readiness claims,
- public launch readiness claims.

The only product store mutation exception is the pre-existing token-gated local reviewed-index rebuild worker, and that worker remains separately governed by LOCAL-09 policy.

