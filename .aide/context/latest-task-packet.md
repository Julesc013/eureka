# AIDE Latest Task Packet

## PHASE

H0-BUNDLE-03 - Coverage ledger, source packs, and connector scorecards

## GOAL

Close the H0 Source OS foundation by adding source coverage ledgers, coverage
manifests, connector scorecards, connector quality deltas, source pack
manifests/exports, no-network helper scripts, tests, docs, and audit evidence.
This task must not enable live source access or accept source truth.

## WHY

H0-BUNDLE-01 defined source governance. H0-BUNDLE-02 defined the reusable
connector interface and fixture replay layer. H0-BUNDLE-03 makes that
foundation measurable and portable so H1 metadata-wave work can start from
reviewed coverage, scorecard, and source-pack artifacts instead of ad hoc
connector notes.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/H0-BUNDLE-03/task.yaml`
- `control/audits/h0-bundle-01-source-os-foundation-v0/`
- `control/audits/h0-bundle-02-connector-interface-replay-v0/`
- `contracts/sources/`
- `contracts/connectors/`
- `contracts/packs/`
- `runtime/connectors/core/`
- `control/inventory/sources/`
- `control/inventory/connectors/`
- `control/inventory/packs/`
- `HUMAN-OBS-REVIEW-01` is a parallel side-lane; it remains human-operated and is
  not modified by H0-BUNDLE-03.

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/H0-BUNDLE-03/**`
- `control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/**`
- `control/inventory/sources/source_coverage_*_policy.json`
- `control/inventory/connectors/connector_scorecard_*policy.json`
- `control/inventory/connectors/connector_scorecard_policy.json`
- `control/inventory/packs/source_pack_*_policy.json`
- `contracts/sources/source_coverage_ledger.v0.json`
- `contracts/sources/source_coverage_manifest.v0.json`
- `contracts/connectors/connector_scorecard.v0.json`
- `contracts/connectors/connector_quality_delta.v0.json`
- `contracts/packs/source_pack_manifest.v0.json`
- `contracts/packs/source_pack_export.v0.json`
- `runtime/connectors/core/coverage_ledger.py`
- `runtime/connectors/core/connector_scorecard.py`
- `runtime/connectors/core/source_pack.py`
- `examples/source_coverage/**`
- `examples/connectors/core/scorecards/**`
- `examples/source_packs/**`
- `scripts/record_source_coverage.py`
- `scripts/build_source_pack.py`
- `scripts/score_connector.py`
- `scripts/validate_source_os_coverage_scorecards.py`
- `scripts/audit_h0_integration.py`
- `tests/connectors/test_source_os_coverage_scorecards.py`
- `tests/operations/test_source_os_coverage_scorecard_scripts.py`
- `tests/operations/test_h0_integration_audit.py`
- `docs/reference/SOURCE_COVERAGE_LEDGER.md`
- `docs/reference/SOURCE_COVERAGE_MANIFEST.md`
- `docs/reference/CONNECTOR_SCORECARD_CONTRACT.md`
- `docs/reference/SOURCE_PACK_MANIFEST_CONTRACT.md`
- `docs/architecture/SOURCE_COVERAGE_MODEL.md`
- `docs/architecture/CONNECTOR_SCORECARD_MODEL.md`
- `docs/architecture/SOURCE_PACK_MODEL.md`
- `docs/operations/SOURCE_COVERAGE_REVIEW.md`
- `docs/operations/CONNECTOR_SCORECARD_REVIEW.md`
- `docs/operations/SOURCE_PACK_EXPORT_REVIEW.md`
- `docs/operations/H0_SOURCE_OS_INTEGRATION_AUDIT.md`

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

The active queue task narrows the H0-BUNDLE-03 exceptions above. Work proceeds
without changing Eureka product behavior.

## IMPLEMENTATION

- Define coverage ledger/manifest, connector scorecard/quality delta, and
  source pack manifest/export contracts.
- Add no-network runtime helpers under `runtime/connectors/core/`.
- Add CLIs for source coverage recording, connector scoring, source-pack
  building, H0 integration audit, and validation.
- Add examples and generated audit evidence for H0 exit and H1 readiness.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_source_os_coverage_scorecards.py`
- `python scripts/record_source_coverage.py --input examples/source_coverage/internet_archive_coverage_record_v0.json --check`
- `python scripts/score_connector.py --input examples/connectors/core/scorecards/internet_archive_scorecard_v0.json --check`
- `python scripts/build_source_pack.py --input examples/source_packs/internet_archive_source_pack_manifest_v0.json --check`
- `python scripts/audit_h0_integration.py --check`
- `python -m unittest tests.connectors.test_source_os_coverage_scorecards`
- `python -m unittest tests.operations.test_source_os_coverage_scorecard_scripts`
- `python -m unittest tests.operations.test_h0_integration_audit`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- Audit pack: `control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/`
- Queue task: `.aide/queue/H0-BUNDLE-03/task.yaml`
- Generated samples under the audit pack plus `examples/source_coverage/**`,
  `examples/connectors/core/scorecards/**`, and `examples/source_packs/**`

## NON_GOALS

- No live source calls, API calls, source sync, downloads, scraping, crawling,
  public query fanout, model calls, public/master index mutation, evidence or
  candidate acceptance, source-pack import/submission, rights clearance,
  malware safety, installability, exhaustive-coverage, external-superiority, or
  production-readiness claims.
- No changes to `HUMAN-OBS-REVIEW-01`; that remains a parallel human
  observation side-lane.

## ACCEPTANCE

- Contracts, policies, runtime helpers, scripts, examples, docs, tests, and
  audit evidence exist and validate offline.
- H0 integration audit and H1 readiness recommendation exist.
- No new live source access or product behavior change is enabled.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED`, `VALIDATION`, `H0_EXIT`,
`H1_READINESS`, `RISKS`, and `NEXT TASK`.

## TOKEN_ESTIMATE

approx_tokens: 1700
