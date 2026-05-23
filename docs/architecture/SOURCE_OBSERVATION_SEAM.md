# Source Observation Seam

R0-04 adds `runtime/source/observation/` as the first clean product runtime seam for source metadata observation.

The package exists because earlier H-series connector work proved useful policies and fixtures, but those modules are named around task phases. Product runtime needs a domain-shaped boundary that later stores, review code, and index rebuilds can consume without importing phase-specific scaffolding.

## Lifecycle

The seam models this local, in-memory lifecycle:

1. `SourceRecord` describes a source, its family, trust lane, locators, capabilities, and limits.
2. `SourcePolicy` and `PolicyDecision` describe whether a requested metadata operation is allowed, blocked, review-bound, or not evaluable.
3. `MetadataRequest` describes intended metadata observation.
4. `MetadataResponse` describes already-obtained payload material supplied by the caller.
5. `SourceObservation` records observed source fields with a response fingerprint and confidence.
6. `NormalizedObservation` keeps candidate normalized fields without accepting product truth.
7. `EvidenceCandidate` carries a candidate claim and remains unaccepted.
8. `ReviewItem` creates review work without making a review decision.

## What It Does Not Do

R0-04 does not perform live calls, source sync, downloads, durable writes, review persistence, public index writes, master index writes, connector registry mutation, or site regeneration.

It also does not rewrite `runtime/connectors/` or retire the historical H-series fixture modules. Those modules remain compatibility and evidence material until later recovery tasks replace or quarantine them.

## Relationship To Later Seams

R0-05 can use this package as the input boundary for a durable source cache. R0-06 can use `EvidenceCandidate` as the input boundary for a durable evidence ledger. R0-07 can use `ReviewItem` as the input boundary for a review queue. R0-08 can rebuild a reviewed public index only after candidates receive explicit review decisions.

## Naming Boundary

Product objects are named by domain role:

- `SourceRecord`
- `SourcePolicy`
- `MetadataRequest`
- `MetadataResponse`
- `SourceObservation`
- `NormalizedObservation`
- `EvidenceCandidate`
- `ReviewItem`
- `ConnectorHealth`

Runtime payloads must not expose task, prompt, audit, bundle, or boundary-check vocabulary. The validator scans the runtime package and product contracts for those terms.

## Compatibility Plan

Old H-series fixture code is not imported by this seam. Future tasks should migrate behavior by domain role:

- source configs become `SourceRecord` and `SourcePolicy`
- request builders become `MetadataRequest`
- observed payloads become `MetadataResponse`
- normalization results become `NormalizedObservation`
- review previews become `ReviewItem`

The migration order is source cache, evidence ledger, review queue, then reviewed index rebuild.
