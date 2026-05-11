# H14 Source Reliability Freshness Candidate

H14-BUNDLE-02 is fixture-runtime work for the Source OS rollup. It reads only committed synthetic fixtures and normalizes them into candidate and preview outputs.

It is not source discovery, source approval, connector approval, pack import/export, registry mutation, source-cache write, evidence write, public-index write, master-index write, production readiness, launch readiness, or public truth acceptance.

Outputs remain candidates: SourceNeed, SourceCandidate, source discovery, source pack manifest, connector pack manifest, coverage manifest, connector scorecard, reliability/freshness, dispute/revocation, lineage/provenance, pack import/export boundary, source-cache preview, evidence preview, and fixture replay report.

Required boundaries: no live calls, no network/API/model/provider/browser calls, no crawling, no scraping, no source sync, no local/private/authenticated/restricted access, no pack export/import/signing/publication/acceptance, no registry mutation, and no source/evidence/candidate/public truth acceptance.

Validation:

```bash
python scripts/validate_h14_source_discovery_fixture_runtime.py
python scripts/replay_h14_source_discovery_fixtures.py --check
python scripts/summarize_h14_source_discovery_fixture_outputs.py --input examples/connectors/h14_source_discovery --check
```
