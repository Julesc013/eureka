# Validation

## H2 Required Commands

- PASS: `git status --short`
- PASS: `git diff --check` with line-ending warnings only.
- PASS: `python -m json.tool ...` for all H2-BUNDLE-02 contracts, policies, and report JSON.
- PASS: `python scripts/validate_h2_package_registry_fixture_runtime.py`
- PASS: `python scripts/normalize_h2_package_fixture.py --source-id crates_io --input examples/connectors/h2_package_registries/fixtures/crates_io/typical_record.json --check`
- PASS: `python scripts/replay_h2_package_fixtures.py --check`
- PASS: `python scripts/summarize_h2_package_fixture_outputs.py --input examples/connectors/h2_package_registries --check`
- PASS: `python -m unittest tests.connectors.test_h2_package_fixture_runtime`
- PASS: `python -m unittest tests.connectors.test_h2_package_identity_mapping`
- PASS: `python -m unittest tests.operations.test_h2_package_fixture_scripts`
- PASS: `python -m unittest discover -s tests -t .` (2920 tests)
- PASS: `python scripts/check_architecture_boundaries.py`

## Existing Validator Lane

- PASS: `python scripts/validate_h2_package_registry_policy_packs.py`
- PASS: requested existing local MVP, public alpha, MVP alpha, hosted wrapper, hosting readiness, native packaging, Track C, relay, snapshot, safe actions, pack quarantine, ranking shadow, search explanation, extraction, H1, H0, IA, local source cache, evidence ledger, bridge, review queue, candidate promotion, pack builder, and pack export validators present locally.

## AIDE Lite Lane

- PASS: `py -3 .aide/scripts/aide_lite.py doctor`
- PASS: `py -3 .aide/scripts/aide_lite.py validate`
- PASS: `py -3 .aide/scripts/aide_lite.py test`
- PASS: `py -3 .aide/scripts/aide_lite.py selftest`
- WARN: `py -3 .aide/scripts/aide_lite.py verify` warning-only diff-scope notes because the latest task packet routes to H2-BUNDLE-03 while this branch carries the H2-BUNDLE-02 implementation diff.
- PASS: `py -3 .aide/scripts/aide_lite.py eval list`
- PASS: `py -3 .aide/scripts/aide_lite.py eval run`
- PASS: `py -3 .aide/scripts/aide_lite.py review-pack`
- PASS: `py -3 .aide/scripts/aide_lite.py adapter validate`

## Boundary Confirmation

- No live source calls, network/API/model/provider/browser calls, package downloads, package-manager invocations, installs, execution, source sync, public search behavior changes, public/master index mutations, or truth acceptance occurred.
