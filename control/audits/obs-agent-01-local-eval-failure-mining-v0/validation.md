# OBS-AGENT-01 Validation

Validation is local only. It must not open browsers, fetch URLs, scrape, crawl, call APIs, call models/providers, create observed files, accept candidates as truth, mark pending slots observed, mutate the index, or modify Track B files.

## Preflight

- PASS: `git status --short` was clean before edits.
- PASS: `git log --oneline -8` showed local Track B commits through TRACK-B-06.
- PASS: `git log --all --oneline --grep "OBS-REPLAN-01"` found `cfe56ecc`.
- PASS: `git log --all --oneline --grep "TRACK-B-01"` found Track B commit evidence.
- PASS: `git log --all --oneline --grep "TRACK-B-02"` found Track B commit evidence.
- WARN: `.aide/context/latest-task-packet.md` points at TRACK-B-06, so OBS-AGENT-01 did not rewrite AIDE queue or latest task packet.

## Required Local Checks

- PASS: `git diff --check`.
- PASS: `python -m json.tool control/inventory/observations/obs_agent_local_eval_failure_mining_policy.json`.
- PASS: `python -m json.tool control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json`.
- PASS: `python -m json.tool control/audits/obs-agent-01-local-eval-failure-mining-v0/obs_agent_01_report.json`.
- PASS: `python scripts/validate_agent_assisted_observation_policy.py`.
- PASS: `python scripts/validate_observation_candidate.py`.
- PASS: `python scripts/mine_local_eval_observation_candidates.py --list-inputs`.
- PASS: `python scripts/mine_local_eval_observation_candidates.py --check`.
- PASS: `python scripts/validate_obs_agent_local_eval_mining.py`.
- PASS: `python scripts/summarize_observation_candidates.py`.
- PASS: `python -m unittest tests.operations.test_obs_agent_local_eval_mining`.
- PASS: `python -m unittest tests.operations.test_agent_assisted_observation_policy`.
- PASS: `python -m unittest tests.contracts.test_observation_candidate_contracts`.
- PASS: `python scripts/check_architecture_boundaries.py`.

## Broader Test Lane

- FAIL: `python3 -m unittest discover -s tests -t .` ran 1929 tests and reported 30 failures and 188 errors.
- Reason: failures are outside the OBS lane and include runtime imports that require `datetime.UTC` on a Python 3.11+ interpreter, plus pre-existing static artifact and checksum drift checks.
- Cleanup: the broad test run deleted generated `site/dist` working-tree files; those deletions were restored and are not part of this task.
- Scope check: OBS-specific tests passed after restore.

## Track Validators

- FAIL: `python scripts/validate_track_a_contracts.py` under local default Python 3.8.1 because the script uses modern type syntax.
- PASS: `python3 scripts/validate_track_a_contracts.py` as the local equivalent.
- PASS: `python scripts/validate_eureka_node_manifest.py`.
- PASS: `python scripts/validate_eureka_node_policy.py`.

## AIDE Lite

The requested `py -3` launcher is not available on this machine. `python3` is Python 3.9.13 and was used as the local equivalent where possible.

- PASS: `python3 .aide/scripts/aide_lite.py doctor`.
- PASS/WARN: `python3 .aide/scripts/aide_lite.py validate`; warnings are optional missing review-packet refs.
- FAIL: `python3 .aide/scripts/aide_lite.py test`; Python 3.9 `Path.write_text` does not support the `newline` keyword used by AIDE Lite.
- FAIL: `python3 .aide/scripts/aide_lite.py selftest`; same Python runtime limitation.
- WARN: `python3 .aide/scripts/aide_lite.py verify`; 0 errors, with expected diff-scope warnings because the active task packet points at TRACK-B-06 rather than OBS-AGENT-01.
- PASS: `python3 .aide/scripts/aide_lite.py eval list`.
- FAIL: `python3 .aide/scripts/aide_lite.py eval run`; same Python runtime limitation.
- FAIL: `python3 .aide/scripts/aide_lite.py review-pack`; same Python runtime limitation.
- PASS: `python3 .aide/scripts/aide_lite.py adapter validate`.

## Boundary Notes

- No live external searches were run.
- No pending observation slot was marked observed.
- No observed result file was created.
- No accepted evidence was created.
- No master index was mutated.
- No Track B file was intentionally modified.
- No Eureka product behavior, public route, hosting, live probe, source connector, source sync, download, upload, account, telemetry, native, rights-clearance, malware-safety, installability, or exhaustive-search claim was added.
