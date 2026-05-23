# Local Review Rebuild Loop

LOCAL-08 adds the first localhost-only operator-gated mutation path for the
Local Appliance. The loop lets an operator inspect local review items, record a
local decision, and rebuild the reviewed public index from accepted review
items.

The loop uses the existing local runtime composition boundary. Service and UI
code open `runtime/local/appliance`, then operate through `review_queue` and
`public_index`; no ad hoc SQLite path is used.

## Boundary

- Mutating routes are localhost-only.
- Mutating routes require an operator token.
- Raw operator tokens are not stored.
- Review decisions update local review queue state only.
- Rebuild writes only to the explicit local reviewed public index store.
- Source cache and evidence ledger input records are not mutated by rebuild.
- Master index, site output, LAN, deployment, source probes, worker execution,
  and model/provider calls remain disabled.

## Non-Claims

A local review decision and a rebuilt reviewed index record are local reviewed
projections. They are not global proof, legal approval, rights clearance,
malware safety, installability certification, exhaustive source coverage,
production readiness, or public launch readiness.

## Handoff

LOCAL-09 can attach a deterministic local worker runner to the durable queue,
but LOCAL-08 does not execute queued work.
