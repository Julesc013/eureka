# Search / Object / Absence Results

Positive query:

- Query: `demo project`
- Result count: `1`
- Returned title: `Demo Project`
- Returned source id: `source.fixture.local.metadata`
- Returned record id: `pir_f4453ae8f3ab6d41`
- Matched terms: `demo`, `project`

Object result:

- Object/result representation uses the public index record produced by the isolated Q58 rebuild.
- Title: `Demo Project`
- Description: `Synthetic local metadata used by the Q58 fixture vertical slice`
- Review decision ref: `rvd_fixture_demo_project_accept_v0`
- Evidence ref: `evc_7a58fa86edc377ef`

Absence query:

- Query: `zzznomatch`
- Result count: `0`
- Checked source: `source.fixture.local.metadata`
- Limitations:
  - local reviewed index only;
  - absence does not prove no matching source exists;
  - absence does not inspect live sources.

Proof command:

- `python scripts/validate_fixture_source_observation_vertical_slice.py --output-root .aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run --output .aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run-report.json --json`: PASS.

