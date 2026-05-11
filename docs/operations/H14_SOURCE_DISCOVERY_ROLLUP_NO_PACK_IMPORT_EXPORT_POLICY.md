# H14 Source Discovery Rollup No-Pack-Import/Export Policy

H14-BUNDLE-03 forbids source pack export/import, connector pack export/import, coverage manifest export/import, record manifest export, evidence pack export, resolution pack export, CAS manifest export, pack signing, pack publication, private pack handling, pack acceptance, registry mutation, source-cache writes, evidence writes, public-index writes, and master-index writes.

H14 rollup dry-runs are committed-artifact-only Source OS aggregation rehearsals. They may produce SourceNeed, SourceCandidate, discovery, pack, coverage, scorecard, reliability/freshness, dispute/revocation, lineage/provenance, source-cache, evidence, review-seed, and health previews.

They are not source discovery runtime, live probes, web search, crawling, scraping, model/provider calls, pack import/export, registry mutation, source-cache persistence, evidence acceptance, public/master index mutation, source approval, connector approval, coverage truth, reliability/freshness truth, dispute/revocation truth, lineage truth, pack truth, production readiness, or launch readiness.

Current inputs are limited to committed H0-H14 policy, fixture, normalized, replay, coverage, scorecard, source-pack, connector-pack, and audit artifacts. Output paths are limited to H14 rollup examples, H14 rollup audit generated output, or explicit temporary test paths.

Validation commands:

```bash
python scripts/validate_h14_source_discovery_rollup_dry_run.py
python scripts/run_h14_source_discovery_rollup_dry_run.py --source-id source_need_registry --request-key example_source_need_rollup --check
python scripts/summarize_h14_source_discovery_rollup_outputs.py --input examples/connectors/h14_source_discovery/rollup_dry_run_results --check
```
