# Q61 Reviewed Index Persistence Audit

## Persistent Index Artifact

- Path: `.aide/queue/EUREKA-REVIEWED-INDEX-PERSISTENCE-01/evidence/fixture-run/reviewed-index-artifact.json`
- Schema: `eureka.fixture_reviewed_index_artifact.v0`
- Artifact id: `ria_fixture_demo_project_v0`
- Builder id: `eureka.fixture_reviewed_index_persistence.v0`
- Record count: 1
- Indexed object id: `pir_f4453ae8f3ab6d41`
- Artifact hash: `sha256:8c96ea8acf85da7c4ce1b40cc3dcd95edd6fa6c54105f75665f6ca79ec3ede23`

## Rebuild Method

Q61 rebuilds the reviewed local fixture index from reviewed fixture inputs and
writes a sorted deterministic JSON artifact to an evidence-local path.

## Deterministic Rebuild

Runtime tests run the fixture slice twice in separate roots and compare the
persisted artifact byte-for-byte. Result: PASS.

## Load / Read Behavior

Q61 load helpers serve:

- positive search from persisted artifact;
- object/detail from persisted artifact;
- evidence/source summary refs from persisted artifact;
- bounded absence from persisted artifact.

## Index Validation

Validation checks required fields, local/fixture markers, accepted-only records,
source/evidence/review refs, no-live flags, and `production_public_index: false`.
Missing/corrupt/non-accepted artifacts produce controlled validation errors.

## Local-Only / Not Public Index Proof

The artifact is under `.aide/queue/**/evidence/fixture-run/`, has fixture/local
markers, and explicitly records `production_public_index: false` and
`public_index_mutation: false`.
