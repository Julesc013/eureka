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
- `notes`

The field set is intentionally descriptive. It is not a final ontology.

## Seed Records In Scope

Source Registry v0 currently seeds:

- `synthetic-fixtures`
- `github-releases-recorded-fixtures`
- `internet-archive-placeholder`
- `wayback-memento-placeholder`
- `software-heritage-placeholder`
- `local-files-placeholder`

The first two are active fixture-backed records. The remaining records are
honest placeholders or future anchors only.

## Public Projection Rules

Public source-registry views may show:

- source id and display name
- family, status, roles, surfaces, and trust lane
- connector label and connector status
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

## Status

Source Registry v0 is now implemented as bounded inventory and metadata only.
It informs future connector planning, UI labeling, and public policy
projection. It does not imply that placeholder sources are usable runtime
connectors today.
