# Local Source Cache Runtime

The local source cache runtime records fixture-only, repo-local source cache records from explicit JSON input. A record may describe source metadata, a source locator, policy posture, coverage, health, limitations, a source lead, or a committed connector fixture output.

The runtime does not fetch sources, call APIs, run connectors, scrape, crawl, download, upload, execute files, create private local state, write evidence records, or mutate any index. Records are source observations and review items, not evidence truth, public truth, rights clearance, malware safety, verified installability, or production readiness.

## Inputs

Current inputs are explicit local JSON records only:

- committed source fixtures, pack examples, static artifacts, audit reports, or public-safe summaries
- source lead candidates
- candidate records
- SearchNeed records
- WorkUnitResult records
- node policy evaluation records
- source cache record examples

Forbidden inputs include live source results, scraped results, private files, secrets, account/session material, telemetry streams, executable downloads, installer payloads, browser profiles, and unreviewed API payloads.

## Outputs

Scripts write no files by default. With an explicit `--output`, reports may be written only under `control/audits/**/generated/` or an explicit temporary test directory. The runtime can produce a source cache record, source cache summary, or source cache snapshot. Future evidence-candidate or review-item outputs remain review-gated.

## Boundaries

Every current record preserves:

- `source_cache_record_is_public_truth: false`
- `source_cache_record_is_accepted_evidence: false`
- `source_cache_record_can_mutate_master_index: false`
- `human_review_required_for_downstream_use: true`

Product-boundary fields for network, live probes, source sync, source connectors, downloads, uploads, accounts, telemetry, model providers, review runtime, and master-index mutation remain false.

## Commands

```bash
python scripts/record_source_cache.py --input examples/source_cache_records/source_lead_record_v0.json --check
python scripts/summarize_source_cache.py --input examples/source_cache_records --check
python scripts/validate_local_source_cache_runtime.py
```
