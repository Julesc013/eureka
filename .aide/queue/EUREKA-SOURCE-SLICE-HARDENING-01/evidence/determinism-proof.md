# Determinism Proof

Deterministic fixture inputs:

- Fixture timestamp: `2026-05-12T00:00:00Z`
- Response timestamp: `2026-05-12T00:00:01Z`
- Fixture source id: `source.fixture.local.metadata`
- Fixture artifact id: `fixture.demo-project`
- Positive query: `demo project`
- Absence query: `zzznomatch`

Stable outputs proved by tests:

- Metadata request id: `req_38dbc1939d27f495`
- Metadata response id: `res_1aeee170841e6d56`
- Source observation id: `obs_f784e76abbff8837`
- Normalized observation id: `norm_c8d2a070b535533a`
- Source cache entry id: `sce_166f90a6738492c5`
- Evidence candidate id: `evc_7a58fa86edc377ef`
- Review item id: `rvi_eba5b8afd11a4cf4`
- Review decision id: `rvd_fixture_demo_project_accept_v0`
- Reviewed index record id: `pir_f4453ae8f3ab6d41`

Test refs:

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_fixture_ids_are_deterministic_across_runs`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_full_fixture_loop_produces_search_and_absence_outputs`

Remaining nondeterminism:

- Store event `created_at` / `updated_at` fields use runtime time for persistence events.
- This is acceptable for Q59 because identity, fixture payload, search result, absence query, and local-output behavior are deterministic.
