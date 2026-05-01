# Query Intelligence Plane

Status: contract-only in P59.

The Query Intelligence Plane is the future layer that lets Eureka learn from
public search demand without turning public queries into surveillance or
authoritative truth. Its first contract is the P59 query observation record.

The core doctrine is fast learning, slow truth:

- Public queries may eventually produce privacy-filtered aggregate learning.
- Query observation is not telemetry runtime.
- Query observation is not persistent query logging.
- Query observation is not a result cache, miss ledger, probe queue, candidate
  index, or master-index mutation.
- Public query learning cannot become object truth without later evidence and
  validation gates.

## P59 Boundary

P59 defines `contracts/query/query_observation.v0.json`, a synthetic example,
validators, docs, and an optional dry-run helper that writes nothing. It does
not wire the public search runtime to write observations.

Hard guarantees for P59:

- no runtime persistence
- no telemetry
- no public query logging
- no raw private-looking query publication
- no probe queue
- no shared result cache mutation
- no miss ledger mutation
- no candidate index mutation
- no local index mutation
- no master-index mutation
- no external calls or live probes

## Future Path

Future milestones may define shared query/result cache, search miss ledger,
search need record, probe queue, candidate index, candidate promotion policy,
query privacy and poisoning guard, and demand dashboard. Each must preserve the
separation between observed demand and accepted truth.
