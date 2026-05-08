# Local Foundry State Contract

`contracts/node/local_foundry_state.v0.json` defines the first Eureka Local
Foundry State envelope.

## What It Is

Local foundry state is future private/local state for Eureka Nodes, WorkUnits,
observation candidates, source leads, local candidate drafts, source-cache
drafts, evidence-ledger drafts, review queues, and pack-builder drafts.

The contract records state kind, path policy, privacy posture, Git tracking
rules, reset/delete behavior, export rules, review gates, truth boundaries, and
product-boundary non-claims.

## What It Is Not

Local foundry state is not public truth, accepted evidence, the master index,
hosted product state, a node runtime, a WorkUnit runtime, a review runtime,
source sync, live probing, source connector behavior, telemetry, rights
clearance, malware safety, verified installability, exhaustive search proof, or
production readiness.

## State Kinds

Allowed state kinds include node reports, WorkUnit run reports, WorkUnit
results, dry-run reports, validation reports, observation candidates, review
decisions, source leads, SearchNeed seeds, WorkUnit seeds, candidate drafts,
evidence drafts, source-cache drafts, evidence-ledger drafts, review queue
drafts, pack-builder drafts, pack export drafts, local index previews,
snapshot previews, relay previews, and future private user notes.

Forbidden state kinds include credentials, account sessions, telemetry streams,
private user files, browser profiles, executable downloads, installer payloads,
accepted public records, accepted evidence truth, master-index records, rights
clearance, malware safety, verified installability, exhaustive search proof,
and production readiness claims.

## Path Policy

Future private roots are policy references only. The contract may reference
`.aide.local/eureka/`, `.local/eureka/`, `.cache/eureka/`, `.tmp/eureka/`, and
reviewed audit-generated report paths, but this milestone does not create those
roots or write private state.

Canonical product, contract, runtime, surface, publication, source, accepted
observation, and master-index-adjacent roots remain forbidden for private
foundry state.

## Export And Review

Private foundry state is not exported by default. Public export, pack export,
evidence use, candidate promotion, and master-index import require later
review. Automatic public export, automatic evidence acceptance, and automatic
master-index import are forbidden.

## Validation

Run:

```powershell
python scripts/validate_local_foundry_state.py
```

The validator is stdlib-only, read-only, and must not create local state.
