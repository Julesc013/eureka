# AIDE Latest Task Packet

## PHASE

H1-BUNDLE-04 - First metadata wave review integration and quality delta

## GOAL

Close the first H1 metadata wave by integrating explicit fixture replay outputs and blocked live-probe evidence into offline review previews, quality delta, source-pack update previews, connector-wave postmortem, and H1 exit-gate audit evidence.

H1-BUNDLE-04 does not perform live calls. It routes the repo toward F-BUNDLE-01 when fixture-equivalent H1 outputs are sufficient.

## WHY

H1-BUNDLE-01 added policy packs, H1-BUNDLE-02 added fixture normalizers and replay outputs, and H1-BUNDLE-03 added fail-closed live-probe envelopes. H1-BUNDLE-04 turns those artifacts into review and quality evidence without accepting truth or mutating runtime state.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/H1-BUNDLE-04/task.yaml`
- `control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/`
- `control/audits/h1-bundle-02-metadata-fixture-runtime-v0/`
- `control/audits/h1-bundle-03-metadata-live-probes-v0/`
- `runtime/connectors/h1_metadata_wave/`
- `examples/connectors/h1_metadata_wave/`
- `HUMAN-OBS-REVIEW-01` is a parallel side-lane and is not modified by H1-BUNDLE-04.

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/queue/index.yaml`
- `.aide/queue/H1-BUNDLE-04/**`
- `contracts/connectors/h1_review_integration_result.v0.json`
- `contracts/connectors/h1_quality_delta_report.v0.json`
- `contracts/connectors/h1_connector_wave_postmortem.v0.json`
- `contracts/connectors/h1_integration_audit.v0.json`
- `control/inventory/connectors/h1_review_integration_policy.json`
- `control/inventory/connectors/h1_review_output_policy.json`
- `control/inventory/connectors/h1_review_path_policy.json`
- `control/inventory/connectors/h1_review_truth_policy.json`
- `control/inventory/connectors/h1_quality_delta_policy.json`
- `control/inventory/connectors/h1_connector_wave_postmortem_policy.json`
- `control/inventory/connectors/h1_integration_audit_policy.json`
- `control/audits/h1-bundle-04-review-quality-audit-v0/**`
- `runtime/connectors/h1_metadata_wave/review_integration.py`
- `runtime/connectors/h1_metadata_wave/quality_delta.py`
- `runtime/connectors/h1_metadata_wave/wave_postmortem.py`
- `scripts/integrate_h1_metadata_review.py`
- `scripts/summarize_h1_quality_delta.py`
- `scripts/audit_h1_metadata_wave.py`
- `scripts/validate_h1_review_quality_audit.py`
- `docs/reference/H1_METADATA_REVIEW_INTEGRATION.md`
- `docs/reference/H1_METADATA_QUALITY_DELTA_REPORT.md`
- `docs/reference/H1_CONNECTOR_WAVE_POSTMORTEM.md`
- `docs/architecture/H1_REVIEW_INTEGRATION_MODEL.md`
- `docs/operations/H1_METADATA_WAVE_POSTMORTEM.md`
- `docs/operations/H1_METADATA_WAVE_QUALITY_DELTA.md`
- `docs/operations/H1_TO_EXTRACTION_HANDOFF.md`
- `examples/connectors/h1_metadata_wave/review_integration/**`
- `tests/connectors/test_h1_review_integration_quality.py`
- `tests/operations/test_h1_review_quality_scripts.py`
- `tests/operations/test_h1_integration_audit.py`

## FORBIDDEN_PATHS

- `runtime/**`
- `contracts/**`
- `connectors/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `packaging/**`
- `third_party/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `control/inventory/publication/**`
- `control/inventory/sources/**`
- `.git/**`
- `.env`
- `.env.*`
- `secrets/**`
- `.aide.local/**`

The active queue task narrows H1-BUNDLE-04 exceptions above to the explicit review, quality, and audit paths listed under allowed paths. Work proceeds without changing Eureka product behavior.

## IMPLEMENTATION

- Add H1 review integration, quality delta, connector-wave postmortem, and integration-audit contracts.
- Add H1 review output, path, truth, quality-delta, postmortem, and audit policies.
- Add pure offline H1 review integration, quality delta, and postmortem helpers.
- Add CLIs, validator, examples, audit pack, docs, and tests.
- Recommend F-BUNDLE-01 if H1 fixture-equivalent outputs are sufficient.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_h1_review_quality_audit.py`
- `python scripts/integrate_h1_metadata_review.py --input-dir examples/connectors/h1_metadata_wave/replay_results --check`
- `python scripts/summarize_h1_quality_delta.py --input-dir examples/connectors/h1_metadata_wave/review_integration --check`
- `python scripts/audit_h1_metadata_wave.py --check`
- `python -m unittest tests.connectors.test_h1_review_integration_quality`
- `python -m unittest tests.operations.test_h1_review_quality_scripts`
- `python -m unittest tests.operations.test_h1_integration_audit`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- Existing H1/H0/IA/core validators listed in the task prompt
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval list`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py adapter validate`

## EVIDENCE

- Audit pack: `control/audits/h1-bundle-04-review-quality-audit-v0/`
- Queue task: `.aide/queue/H1-BUNDLE-04/task.yaml`
- Examples under `examples/connectors/h1_metadata_wave/review_integration/`

## NON_GOALS

- No new live source calls by default, broad source search, unbounded API use, source sync, public query fanout, scraping, crawling, package/release/source/archive/WARC/exploit downloads, arbitrary URL fetch, model/provider calls, browser automation, public/master index mutation, evidence/candidate/source/public truth acceptance, source-pack import/submission/acceptance, hosting, telemetry, production-readiness claims, external superiority claims, automatic future connector approval, or local private-state roots.

## ACCEPTANCE

- H1 review integration, quality delta, postmortem, and audit artifacts exist and validate offline.
- H1 exit gate is explicit.
- Next phase recommendation is explicit.
- No public/master index mutation, truth acceptance, product behavior change, live call, or download occurs.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `COMMITS`, `H1_EXIT`, `NEXT_PHASE`, `CHANGED`, `VALIDATION`, `RISKS`, and `NEXT TASK`.

## TOKEN_ESTIMATE

approx_tokens: 1900
