# AIDE Latest Task Packet

## PHASE

H1-BUNDLE-02 - First metadata wave fixture runtimes and normalizers

## GOAL

Add fixture-only normalizers and replayable connector outputs for the first H1
metadata wave: Wayback/CDX/Memento, GitHub Releases, PyPI, npm, Software
Heritage, Repology, and OSV.

This bundle converts committed fixtures into normalized metadata records,
source-cache candidate previews, evidence candidate previews, connector output
envelopes, and fixture replay reports. It does not perform live source access.

## WHY

H0-BUNDLE-02 created the reusable fixture replay envelope, and H1-BUNDLE-01
created policy packs and no-live gates. H1-BUNDLE-02 proves that the seven
source shapes can be parsed from committed public-safe fixtures before any
approved live probe or source sync is considered.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/H1-BUNDLE-02/task.yaml`
- `control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/`
- `contracts/connectors/`
- `runtime/connectors/core/`
- `control/inventory/source_packs/`
- `examples/connectors/h1_metadata_wave/`
- `docs/operations/H1_METADATA_WAVE_FIXTURE_PLAN.md`
- `HUMAN-OBS-REVIEW-01` is a parallel side-lane; it remains human-operated and is not modified by H1-BUNDLE-02.

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/queue/index.yaml`
- `.aide/queue/H1-BUNDLE-02/**`
- `contracts/connectors/h1_metadata_fixture.v0.json`
- `contracts/connectors/h1_metadata_normalized_record.v0.json`
- `contracts/connectors/h1_metadata_fixture_replay_result.v0.json`
- `control/inventory/connectors/h1_metadata_*_policy.json`
- `control/audits/h1-bundle-02-metadata-fixture-runtime-v0/**`
- `runtime/connectors/h1_metadata_wave/**`
- `scripts/normalize_h1_metadata_fixture.py`
- `scripts/replay_h1_metadata_fixtures.py`
- `scripts/validate_h1_metadata_fixture_runtime.py`
- `docs/reference/H1_METADATA_FIXTURE_RUNTIME.md`
- `docs/reference/H1_METADATA_NORMALIZED_RECORD.md`
- `docs/architecture/H1_METADATA_NORMALIZER_MODEL.md`
- `docs/operations/H1_METADATA_FIXTURE_REPLAY.md`
- `docs/operations/H1_METADATA_FIXTURE_NO_LIVE_CALL_POLICY.md`
- `examples/connectors/h1_metadata_wave/fixtures/**`
- `examples/connectors/h1_metadata_wave/normalized/**`
- `examples/connectors/h1_metadata_wave/replay_results/**`
- `tests/connectors/test_h1_metadata_fixture_runtime.py`
- `tests/operations/test_h1_metadata_fixture_scripts.py`

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

The active queue task narrows the H1-BUNDLE-02 exceptions above to the explicit
contracts and runtime fixture paths listed under allowed paths. Work proceeds
without changing Eureka product behavior.

## IMPLEMENTATION

- Add H1 fixture/normalized/replay contracts.
- Add H1 fixture runtime, normalization, output, path, truth, source-cache, and evidence mapping policies.
- Add fixture-only runtime modules under `runtime/connectors/h1_metadata_wave/`.
- Add committed fixtures, normalized examples, replay results, docs, scripts, tests, and audit evidence.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python scripts/validate_h1_metadata_fixture_runtime.py`
- `python scripts/normalize_h1_metadata_fixture.py --source-id pypi --input examples/connectors/h1_metadata_wave/fixtures/pypi/typical_record.json --check`
- `python scripts/replay_h1_metadata_fixtures.py --check`
- `python -m unittest tests.connectors.test_h1_metadata_fixture_runtime`
- `python -m unittest tests.operations.test_h1_metadata_fixture_scripts`
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

- Audit pack: `control/audits/h1-bundle-02-metadata-fixture-runtime-v0/`
- Queue task: `.aide/queue/H1-BUNDLE-02/task.yaml`
- Generated samples under the audit pack plus fixture examples under `examples/connectors/h1_metadata_wave/**`

## NON_GOALS

- No live source calls, external calls, API calls, network calls, live probes,
  source sync, live connector runtime, downloads, scraping, crawling, public
  query fanout, model/provider calls, public/master index mutation, evidence or
  candidate acceptance, source truth acceptance, source-pack import/submission,
  rights clearance, malware safety, installability, production-readiness claims,
  or changes to `HUMAN-OBS-REVIEW-01`; that remains a parallel human observation
  side-lane.

## ACCEPTANCE

- H1 fixture contracts, policies, normalizers, fixtures, normalized examples,
  replay results, scripts, tests, docs, and audit evidence exist and validate
  offline.
- No live source access or product behavior change is enabled.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED`, `VALIDATION`, `RISKS`, and
`NEXT TASK`.

## TOKEN_ESTIMATE

approx_tokens: 1700
