# AIDE Latest Task Packet

## PHASE

H1-BUNDLE-03 - First metadata wave approved live probes

## GOAL

Add the first H1 metadata-wave bounded live-probe framework for Wayback/CDX/Memento, GitHub Releases, PyPI, npm, Software Heritage, Repology, and OSV.

The current committed posture is blocked-by-default: no source has operator approval for live access, so default execution is offline preflight and `--live` emits blocked results before network.

## WHY

H1-BUNDLE-01 added policy packs and H1-BUNDLE-02 added fixture normalizers. H1-BUNDLE-03 adds the live-boundary envelope so future operator-approved metadata probes can be one-request, metadata-only, review-gated, and safe to audit.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/H1-BUNDLE-03/task.yaml`
- `control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/`
- `control/audits/h1-bundle-02-metadata-fixture-runtime-v0/`
- `runtime/connectors/h1_metadata_wave/`
- `examples/connectors/h1_metadata_wave/`
- `HUMAN-OBS-REVIEW-01` is a parallel side-lane; it remains human-operated and is not modified by H1-BUNDLE-03.

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/queue/index.yaml`
- `.aide/queue/H1-BUNDLE-03/**`
- `contracts/connectors/h1_live_probe_request.v0.json`
- `contracts/connectors/h1_live_probe_result.v0.json`
- `contracts/connectors/h1_live_probe_output_bundle.v0.json`
- `control/inventory/connectors/h1_metadata_live_probe_*.json`
- `control/audits/h1-bundle-03-metadata-live-probes-v0/**`
- `runtime/connectors/h1_metadata_wave/live_probe_*.py`
- `scripts/run_h1_metadata_live_probe.py`
- `scripts/validate_h1_metadata_live_probe.py`
- `scripts/summarize_h1_live_probe_outputs.py`
- `scripts/validate_ia_readiness_polish.py`
- `docs/reference/H1_METADATA_LIVE_PROBE.md`
- `docs/reference/H1_METADATA_LIVE_PROBE_RESULT.md`
- `docs/architecture/H1_METADATA_LIVE_PROBE_MODEL.md`
- `docs/operations/H1_METADATA_LIVE_PROBE_REVIEW.md`
- `docs/operations/H1_METADATA_LIVE_PROBE_APPROVAL_GATES.md`
- `docs/operations/H1_METADATA_LIVE_PROBE_BLOCKED_MODE.md`
- `examples/connectors/h1_metadata_wave/live_probe/**`
- `examples/connectors/h1_metadata_wave/live_probe_results/**`
- `examples/connectors/h1_metadata_wave/live_probe_outputs/**`
- `tests/connectors/test_h1_metadata_live_probe.py`
- `tests/operations/test_h1_metadata_live_probe_scripts.py`
- `tests/operations/test_ia_readiness_polish.py`

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

The active queue task narrows H1-BUNDLE-03 exceptions above to the explicit live-probe framework paths listed under allowed paths. Work proceeds without changing Eureka product behavior.

## IMPLEMENTATION

- Add H1 live-probe request/result/output-bundle contracts.
- Add fail-closed H1 live-probe policies, request manifests, endpoint/rate/cache/kill/output/path/review/truth policies.
- Add source-specific metadata-only wrappers and a shared live-probe common module.
- Add blocked examples, preview outputs, docs, scripts, tests, and audit evidence.
- Update the IA readiness validator narrowly so its historical current-task check accepts legitimate H1 progression while still rejecting stale IA-BUNDLE-00 or sync-baseline packets.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_h1_metadata_live_probe.py`
- `python scripts/run_h1_metadata_live_probe.py --source-id pypi --request-key example_project_metadata --check`
- `python scripts/summarize_h1_live_probe_outputs.py --input examples/connectors/h1_metadata_wave/live_probe_results --check`
- `python -m unittest tests.connectors.test_h1_metadata_live_probe`
- `python -m unittest tests.operations.test_h1_metadata_live_probe_scripts`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- Existing H0/H1/IA/core validators listed in the task prompt
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

- Audit pack: `control/audits/h1-bundle-03-metadata-live-probes-v0/`
- Queue task: `.aide/queue/H1-BUNDLE-03/task.yaml`
- Blocked examples under `examples/connectors/h1_metadata_wave/live_probe*`

## NON_GOALS

- No broad source search, unbounded API use, source sync, public query fanout, scraping, crawling, downloads, arbitrary URL fetch, model/provider calls, browser automation, public/master index mutation, evidence/candidate/source/public truth acceptance, source-pack import/submission, rights clearance, malware safety, installability, production-readiness claims, or changes to `HUMAN-OBS-REVIEW-01`.

## ACCEPTANCE

- H1 live-probe framework exists and validates offline.
- Live probes fail closed unless committed source-specific approval exists.
- Current outputs are blocked because no source has committed live approval.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `COMMITS`, `LIVE_PROBES`, `CHANGED`, `VALIDATION`, `RISKS`, and `NEXT TASK`.

## TOKEN_ESTIMATE

approx_tokens: 1800
