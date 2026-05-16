# Q58 Product Slice Audit

## Fixture Source

- Source id: `source.fixture.local.metadata`
- Source reference: `fixture://q58/demo-project`
- Fixture artifact id: `fixture.demo-project`
- Fixture title: `Demo Project`

## Observation

- Request id: `req_38dbc1939d27f495`
- Response id: `res_1aeee170841e6d56`
- Source observation id: `obs_f784e76abbff8837`
- Response fingerprint: `93288b3fd21918a7317b600452eae7bbfbf3cd1be40f631805e3c73599c64dd7`

## Normalized Observation

- Normalized observation id: `norm_c8d2a070b535533a`
- Source family: `local_fixture`
- Confidence: `0.7`

## Evidence Candidate

- Evidence candidate id: `evc_7a58fa86edc377ef`
- Claim type: `metadata`
- Claim subject/source: `source.fixture.local.metadata`

## Review Decision

- Review item id: `rvi_eba5b8afd11a4cf4`
- Review decision id: `rvd_fixture_demo_project_accept_v0`
- Decision: accepted for local fixture index.

## Reviewed Local Index Candidate

- Record id/object id: `pir_f4453ae8f3ab6d41`
- Search query `demo project` returns one reviewed record.
- Absence query `zzznomatch` returns zero results with bounded absence.

## Tests

- `python -m unittest discover -s tests/runtime -t . -p test_fixture_source_observation_vertical_slice.py`: PASS, now 12 tests after Q61.
- `python -m unittest discover -s tests/operations -t . -p test_fixture_source_observation_vertical_slice_script.py`: PASS, 3 tests.
- `python scripts/validate_fixture_source_observation_vertical_slice.py ... --json`: PASS.

## No-Live / No-Mutation Evidence

Q58 evidence and ECHECK rerun report record all no-live/no-mutation flags as
false and writes only to evidence-local stores under `.aide/queue/**`.
