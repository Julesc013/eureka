# Source Registry Schema

Source Registry v0 is Eureka's first bounded source-control plane.

It makes source knowledge explicit through governed inventory records, a small
draft schema set, a stdlib-only runtime loader, and bounded public projection.
It does not turn source metadata into runtime truth on its own.

## Current Locations

The current Source Registry v0 implementation is split across:

- `contracts/source_registry/` for draft schemas
- `control/inventory/sources/` for governed seed records
- `runtime/source_registry/` for stdlib-only runtime loading and filtering
- `runtime/gateway/public_api/source_registry_boundary.py` for transport-neutral public projection
- `contracts/ui/view_models/source_registry.view_model.yaml` for shared surface projection

## Purpose

The registry answers bounded planning and labeling questions such as:

- what kind of source is this
- what roles does it play
- what surfaces does it expose
- what identifiers does it emit
- what kinds of objects and artifacts does it speak about
- which connector owns it today, if any
- whether it is fixture-backed, placeholder, future, or disabled
- what bounded capabilities are currently available
- how deeply the current source slice is indexed
- what trust lane, authority class, legal posture, and freshness notes are known

## Source Record v0 Field Set

`source_record.schema.yaml` currently standardizes a small bounded field set:

- `source_id`
- `name`
- `source_family`
- `status`
- `roles`
- `surfaces`
- `trust_lane`
- `authority_class`
- `protocols`
- `object_types`
- `artifact_types`
- `identifier_types_emitted`
- `connector`
- `fixture_paths`
- `live_access`
- `extraction_policy`
- `rights_notes`
- `legal_posture`
- `freshness_model`
- `capabilities`
- `coverage`
- `notes`

The field set is intentionally descriptive. It is not a final ontology.

## Capability And Coverage v0

Source Coverage and Capability Model v0 adds compact metadata rather than new
source acquisition behavior.

`capabilities` records booleans for bounded support such as search, item
metadata, file listing, member listing, hashes, content text, action paths,
fixture backing, recorded fixture backing, local-private posture, live support,
and live-deferred posture.

`coverage.coverage_depth` uses this ladder:

0. `source_known`
1. `catalog_indexed`
2. `metadata_indexed`
3. `representation_indexed`
4. `content_or_member_indexed`
5. `action_indexed`

Do not raise a source above its current bounded coverage. Internet Archive,
Wayback/Memento, Software Heritage, and local files remain planning anchors at
`source_known` until a future accepted recorded-fixture or connector milestone
changes their posture.

## Seed Records In Scope

Source Registry v0 currently seeds:

- `synthetic-fixtures`
- `github-releases-recorded-fixtures`
- `internet-archive-placeholder`
- `wayback-memento-placeholder`
- `software-heritage-placeholder`
- `local-files-placeholder`

`synthetic-fixtures` is an active fixture-backed record.
`github-releases-recorded-fixtures` is an active recorded-fixture-backed
record. The remaining records are honest placeholders or future anchors only.

## Public Projection Rules

Public source-registry views may show:

- source id and display name
- family, status, roles, surfaces, and trust lane
- connector label and connector status
- capability summaries, coverage depth, coverage status, connector mode,
  current limitations, and next coverage step
- object and artifact type summaries
- bounded legal, freshness, and notes fields

Public views must not leak:

- raw internal connector implementation details beyond safe labels
- private local filesystem paths
- future auth or credential material

## Explicit Non-Goals

Source Registry v0 does **not** implement:

- live source sync
- crawling
- source health scoring
- trust scoring
- authentication
- async workers
- placeholder connectors
- live probing or crawling
- new source connectors

## Status

Source Registry v0 is now implemented as bounded inventory, capability, and
coverage-depth metadata only. It informs future connector planning, UI labeling,
and public policy projection. It does not imply that placeholder sources are
usable runtime connectors today.
