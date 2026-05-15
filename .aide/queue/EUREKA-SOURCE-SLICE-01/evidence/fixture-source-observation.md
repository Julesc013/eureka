# Fixture Source Observation

Fixture source:

- Source id: `source.fixture.local.metadata`
- Source family: `local_fixture`
- Trust lane: `synthetic_fixture`
- Fixture reference: `fixture://q58/demo-project`
- Artifact id: `fixture.demo-project`
- Title: `Demo Project`
- Version: `1.0.0`
- Fixture timestamp: `2026-05-12T00:00:00Z`
- Response timestamp: `2026-05-12T00:00:01Z`

Generated observation:

- Observation id: `obs_f784e76abbff8837`
- Normalized observation id: `norm_c8d2a070b535533a`
- Response fingerprint: `sha256:93288b3fd21918a7317b600452eae7bbfbf3cd1be40f631805e3c73599c64dd7`
- Confidence: `0.7`

Evidence:

- Full report: `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run-report.json`
- Isolated source cache store: `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/source-cache.sqlite`

No-live proof:

- The fixture payload contains `external_call_performed: false`.
- The source capability limitations include `fixture payload only` and `no live request`.
- Focused tests run the slice with socket creation blocked.
- The Q58 report records `network_calls: false`, `live_source_probes: false`, and `provider_model_calls: false`.

