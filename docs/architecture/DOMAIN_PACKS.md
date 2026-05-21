# DOMAIN Packs

DOMAIN packs describe how a query family should be interpreted before the
generic artefact-resolution kernel does its normal work. They are not truth and
they do not replace source records, evidence ledgers, reviewed records, or
operator review.

The first seed set is fixture-only:

- legacy software
- driver/support media
- frontier-resolution media
- manuals/docs/scans
- package/source release
- web archive traces
- games/emulation
- hardware/firmware support

Each pack can influence query compilation, source-family preferences, expected
Workbench result lanes, draft SearchNeed seeds, draft WorkUnit seeds, review
hints, and action posture. The packs cannot accept evidence, create reviewed
records, mutate indexes, bypass policy, enable no live source behavior, become
connectors, or claim production/public readiness.

Unsafe actions remain blocked by default: downloads, uploads, extraction,
execute/install, model/provider calls, public fanout, source probes, deployment,
operator-instance mutation, and master-index mutation.

Examples under `examples/domain/` are seed packs, not canonical registry truth.
Future SCOUT, F0, and ranking work can consume these hints only through explicit
contracts and validators.
