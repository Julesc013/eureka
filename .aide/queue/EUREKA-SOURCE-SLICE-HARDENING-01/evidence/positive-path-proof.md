# Positive Path Proof

Fixture:

- Source: `source.fixture.local.metadata`
- Artifact: `fixture.demo-project`
- Title: `Demo Project`
- Source reference: `fixture://q58/demo-project`

Behavior:

1. `MetadataRequest` and `MetadataResponse` are built from local fixture data.
2. `build_source_observation` produces `obs_f784e76abbff8837`.
3. `normalize_metadata_response` produces `norm_c8d2a070b535533a`.
4. `build_cache_entry` creates `sce_166f90a6738492c5` in an isolated local source-cache store.
5. `build_evidence_candidate` creates `evc_7a58fa86edc377ef`.
6. Review queue records accepted local-only decision `rvd_fixture_demo_project_accept_v0`.
7. Public index rebuild includes one local reviewed record `pir_f4453ae8f3ab6d41`.
8. Search query `demo project` returns that record.
9. Object result contains matching source, evidence, review, and index refs.

Test refs:

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_full_fixture_loop_produces_search_and_absence_outputs`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_validate_report_rejects_mismatched_refs_and_mutation_flags`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py::test_validator_script_writes_report_and_prints_json`

Evidence:

- `.aide/queue/EUREKA-SOURCE-SLICE-HARDENING-01/evidence/fixture-run-report.json`
