# AIDE Latest Task Packet

## PHASE

H1-BUNDLE-01 - First metadata wave source policy packs

## GOAL

Add policy-pack-only source records, connector-family mappings, approval gates,
fixture requirements, output/truth/no-live policies, coverage previews,
scorecard previews, source-pack manifests, docs, validators, tests, and audit
evidence for the first H1 metadata wave: Wayback/CDX/Memento, GitHub Releases,
PyPI, npm, Software Heritage, Repology, and OSV.

## WHY

H0 closed the reusable Source OS foundation through H0-BUNDLE-01,
H0-BUNDLE-02, and H0-BUNDLE-03. H1-BUNDLE-01 starts the first metadata wave by
describing each source through the H0 vocabulary before any fixture runtime,
live probe, or source sync exists.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/H1-BUNDLE-01/task.yaml`
- `control/audits/h0-bundle-01-source-os-foundation-v0/`
- `control/audits/h0-bundle-02-connector-interface-replay-v0/`
- `control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/`
- `contracts/sources/`
- `contracts/connectors/`
- `contracts/packs/`
- `control/inventory/sources/`
- `control/inventory/connectors/`
- `control/inventory/packs/`
- `runtime/connectors/core/`
- `HUMAN-OBS-REVIEW-01` is a parallel side-lane; it remains human-operated and is not modified by H1-BUNDLE-01.

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/H1-BUNDLE-01/**`
- `control/inventory/source_packs/**`
- `control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/**`
- `examples/source_packs/h1_metadata_wave_source_pack_manifest_v0.json`
- `examples/source_packs/h1_metadata_wave_policy_pack_v0.json`
- `examples/source_packs/h1_metadata_wave_source_pack_preview_v0.json`
- `examples/sources/source_records/wayback_cdx_memento_source_v2.json`
- `examples/sources/source_records/github_releases_source_v2.json`
- `examples/sources/source_records/pypi_source_v2.json`
- `examples/sources/source_records/npm_registry_source_v2.json`
- `examples/sources/source_records/software_heritage_source_v2.json`
- `examples/sources/source_records/repology_source_v2.json`
- `examples/sources/source_records/osv_source_v2.json`
- `examples/connectors/h1_metadata_wave/**`
- `docs/reference/H1_METADATA_WAVE_SOURCE_PACKS.md`
- `docs/architecture/H1_METADATA_WAVE_MODEL.md`
- `docs/operations/H1_METADATA_WAVE_POLICY_GATES.md`
- `docs/operations/H1_METADATA_WAVE_NO_LIVE_CALL_POLICY.md`
- `docs/operations/H1_METADATA_WAVE_FIXTURE_PLAN.md`
- `scripts/validate_h1_metadata_wave_policy_packs.py`
- `scripts/summarize_h1_metadata_wave_sources.py`
- `tests/operations/test_h1_metadata_wave_policy_packs.py`
- `tests/operations/test_h1_metadata_wave_summary.py`

## FORBIDDEN_PATHS

- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `control/inventory/publication/**`
- `.git/**`
- `.env`
- `.env.*`
- `secrets/**`
- `.aide.local/**`

The active queue task narrows the H1-BUNDLE-01 exceptions above. Work proceeds
without changing Eureka product behavior.

## IMPLEMENTATION

- Add H1 metadata-wave policies and inventories under `control/inventory/source_packs/`.
- Add seven H1 source records, policy packs, coverage previews, and scorecard previews.
- Add H1 source-pack manifest, fixture plan, no-live docs, validator, summary script, tests, and audit evidence.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_h1_metadata_wave_policy_packs.py`
- `python scripts/summarize_h1_metadata_wave_sources.py --check`
- `python -m unittest tests.operations.test_h1_metadata_wave_policy_packs`
- `python -m unittest tests.operations.test_h1_metadata_wave_summary`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- Audit pack: `control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/`
- Queue task: `.aide/queue/H1-BUNDLE-01/task.yaml`
- Generated samples under the audit pack plus H1 examples under `examples/connectors/h1_metadata_wave/**`

## NON_GOALS

- No live source calls, external calls, API calls, source sync, connector runtime,
  downloads, scraping, crawling, public query fanout, model calls, public/master
  index mutation, evidence or candidate acceptance, source-pack import/submission,
  rights clearance, malware safety, installability, production-readiness claims,
  or changes to `HUMAN-OBS-REVIEW-01`; that remains a parallel human observation
  side-lane.

## ACCEPTANCE

- H1 policies, source inventory, source records, policy packs, coverage previews,
  scorecard previews, fixture plan, docs, scripts, tests, and audit evidence exist
  and validate offline.
- No live source access or product behavior change is enabled.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED`, `VALIDATION`, `RISKS`, and
`NEXT TASK`.

## TOKEN_ESTIMATE

approx_tokens: 1650
