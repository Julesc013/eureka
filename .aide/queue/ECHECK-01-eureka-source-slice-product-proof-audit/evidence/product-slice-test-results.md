# Product Slice Test Results

## Targeted Tests

| Command | Result | Notes |
|---|---|---|
| `python -m unittest discover -s tests/runtime -t . -p test_fixture_source_observation_vertical_slice.py` | PASS | 12 tests. |
| `python -m unittest discover -s tests/operations -t . -p test_fixture_source_observation_vertical_slice_script.py` | PASS | 3 tests. |
| `python scripts/validate_fixture_source_observation_vertical_slice.py --output-root .aide/queue/ECHECK-01-eureka-source-slice-product-proof-audit/evidence/fixture-run --output .aide/queue/ECHECK-01-eureka-source-slice-product-proof-audit/evidence/product-slice-run-report.json --json` | PASS | Wrote evidence-local stores and report. |

## Positive Path

- Query: `demo project`
- Result count: 1
- Object id: `pir_f4453ae8f3ab6d41`
- Evidence id: `evc_7a58fa86edc377ef`
- Review decision id: `rvd_fixture_demo_project_accept_v0`

## Absence Path

- Query: `zzznomatch`
- Result count: 0
- Checked source: `source.fixture.local.metadata`
- Absence scope: local fixture reviewed index only.

## Persisted Index

- Artifact id: `ria_fixture_demo_project_v0`
- Artifact schema: `eureka.fixture_reviewed_index_artifact.v0`
- Record count: 1
- Artifact hash:
  `sha256:8c96ea8acf85da7c4ce1b40cc3dcd95edd6fa6c54105f75665f6ca79ec3ede23`
- Search, object lookup, and absence work from the persisted artifact.

## No-Live

Report no-live flags are all false for network, providers/models, live probes,
source sync, production store writes, registry mutation, site deploy, release
publish, and branch mutation.
