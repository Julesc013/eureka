# Source Cache To Evidence Bridge Runtime

The Source Cache to Evidence Bridge is a fixture-only local runtime that reads an explicit source cache record and maps it into one or more reviewable evidence ledger candidate records.

It is not a live source connector, source sync process, evidence acceptance path, public index path, rights review, malware review, installability review, or master-index mutation path.

## Inputs

The bridge accepts explicit JSON source cache records using the local source cache record shape. Current inputs are committed fixtures, repo-local summaries, source leads, policy records, coverage records, locator records, and blocked policy examples.

The bridge rejects source cache records that carry truth-boundary or product-boundary violations. It also preserves policy blocks instead of promoting them.

## Outputs

The bridge may produce:

- `bridge_result`
- `bridge_summary`
- `evidence_candidate_record`
- `provenance_gap_report`
- `conflict_report`
- `review_item_future`

It must not produce public truth, an accepted public record, rights clearance, malware safety, verified installability, exhaustive search proof, production-readiness claims, or master-index mutation.

## Mapping

Current mappings are deterministic:

- `source_metadata` -> `metadata_claim`
- `source_locator` -> `source_observation`
- `source_policy_record` -> `source_observation`
- `source_health_record` -> `metadata_claim`
- `source_coverage_record` -> `metadata_claim`
- `source_lead_record` -> `source_observation`
- `connector_fixture_record` -> `source_observation`
- `source_identity_record` -> `identity_claim`
- `source_limitations_record` -> `metadata_claim`

Every output remains review-gated.

## Boundaries

The runtime is standard-library only and does not call networks, APIs, models, providers, browsers, crawlers, scrapers, downloaders, uploaders, telemetry, or accounts. It writes only when a script receives an explicit allowed output path under audit generated output or a temp test directory.

Validation:

```bash
python scripts/validate_source_cache_to_evidence_bridge.py
python scripts/bridge_source_cache_to_evidence.py --input examples/source_cache_records/source_metadata_record_v0.json --check
```
