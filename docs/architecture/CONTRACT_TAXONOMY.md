# Contract Taxonomy

`contracts/` is for stable product boundaries. A schema belongs there only when
runtime, APIs, snapshots, native clients, public surfaces, or durable stores
consume or emit it as part of product behavior.

`control/schemas/` is for repo-control schemas: audit reports, fixture replay
records, previews, validator inputs, task packets, queue records, generated
scaffold, and deprecated planning artifacts. Those schemas can be useful and
well-tested without being product contracts.

## Product Contracts

Product contracts describe stable domain or runtime concepts:

- domain objects and identity records
- runtime request/response envelopes
- public API payloads
- snapshot formats
- native client payloads
- durable store events and records
- connector interface envelopes and source policy documents

Product contracts must have a stable owner, compatibility expectations, a
versioning rule, and a validation path. They must not be named after task IDs,
prompt IDs, bundle IDs, audit phases, or generated work packets.

Good product contract placement:

- `contracts/domain/source_record.v0.json`
- `contracts/runtime/source_observation.v0.json`
- `contracts/stores/evidence_event.v0.json`
- `contracts/api/search_result.v0.json`

## Control Schemas

Control schemas describe how the repo is operated, audited, or tested. They may
include task IDs, audit bundle IDs, preview-only wording, fixture-only wording,
or boundary assertions because they are not product semantics.

Control target roots:

- `control/schemas/audits/`
- `control/schemas/fixtures/`
- `control/schemas/previews/`
- `control/schemas/policies/`
- `control/schemas/validators/`
- `control/schemas/tasks/`
- `control/schemas/deprecated/`

## Audit, Fixture, Preview

An audit schema records evidence about work that happened. It is not a product
API, even when it is machine-readable.

A fixture schema describes committed test data or replay results. It can be an
oracle for tests, but it is not proof that runtime behavior exists.

A preview schema describes a candidate, dry run, projected output, or future
review item. It can prepare a product loop, but it is not the loop itself.

## Naming Rules

Use domain vocabulary in product contracts:

- `source_record`
- `source_observation`
- `metadata_request`
- `metadata_response`
- `source_policy`
- `evidence_event`
- `review_item`
- `search_result`

Do not use task or audit vocabulary in product contracts:

- `h14`
- `bundle`
- `quality_delta`
- `next_phase`
- `integration_audit`
- `fixture_replay`
- `truth_boundary`
- `product_boundary`

## Versioning And Compatibility

Product contracts use explicit versions and preserve compatibility until a
reviewed migration updates consumers. Moving a product contract requires a
reference update plan and, when needed, a compatibility shim or alias.

Control schemas may also be versioned, but their compatibility promise is
scoped to validators and audit evidence. They should not be used to imply
runtime readiness.

## Deprecation And Quarantine

Generated scaffold, empty schemas, deprecated planning files, and unknown
contract-like artifacts should be quarantined before deletion. Deletion requires
a later reference audit that proves the file is unreferenced and no validator
depends on it.

## Placement Examples

Bad:

- `contracts/connectors/h14_source_discovery_quality_delta_report.v0.json`
- `contracts/connectors/h1_metadata_fixture_replay_result.v0.json`
- `contracts/audits/local_mvp_next_task_decision.v0.json`

Better:

- `control/schemas/audits/h14/source_discovery_quality_delta_report.v0.json`
- `control/schemas/fixtures/source_metadata/fixture_replay_result.v0.json`
- `control/schemas/tasks/local_mvp_next_task_decision.v0.json`

Good product contract:

- `contracts/domain/source_record.v0.json`
- `contracts/runtime/source_observation.v0.json`
- `contracts/stores/evidence_event.v0.json`
- `contracts/api/search_result.v0.json`

R0-03A plans this taxonomy only. R0-03B performs the moves and reference
updates in reviewed batches.
