# Local Foundry State Model

Local foundry state follows the Track B node, policy, capability, WorkUnit, and
WorkUnit result contracts. Those contracts define who may propose work, which
actions are allowed, and how results remain reviewable. Local foundry state
defines where future private drafts may live and how they stay bounded.

## Relationship To Staging

The existing local quarantine and staging planning separates private candidate
work from canonical product truth. Local foundry state keeps that boundary: it
may support future discovery, dry-runs, staging, review, and pack building, but
it must remain resettable, deletable, auditable, and excluded from Git unless a
reviewed export path explicitly allows committed evidence.

## State Flow

Future nodes and WorkUnits may draft local reports, candidates, source leads,
source-cache drafts, evidence-ledger drafts, review queue items, pack-builder
drafts, and local index previews. Those records stay local/private until a
reviewed export converts them into an accepted downstream artifact.

No local foundry record is accepted evidence, public truth, or a master-index
record by itself.

## Runtime Boundary

This model prepares future query observation, candidate store, source cache,
evidence ledger, review queue, and pack builder runtimes. It does not implement
those runtimes, create private roots, execute WorkUnits, call networks, call
models, or mutate the master-index.
