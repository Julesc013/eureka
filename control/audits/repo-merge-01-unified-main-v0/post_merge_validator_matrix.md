# Post-Merge Validator Matrix

| Lane | Command | Result |
| --- | --- | --- |
| Git | `git diff --check` | PASS |
| Git | precise conflict-marker scan | PASS |
| Architecture | `python scripts/check_architecture_boundaries.py` | PASS |
| Track A | `python scripts/validate_track_a_contracts.py` | PASS |
| OBS | `python scripts/validate_agent_assisted_observation_policy.py` | PASS |
| OBS | `python scripts/validate_observation_candidate.py` | PASS |
| OBS | `python scripts/validate_observation_candidate_review_queue.py` | PASS |
| OBS | `python scripts/validate_search_need_seed_candidates.py` | PASS |
| OBS | `python scripts/validate_workunit_seed_candidates.py` | PASS |
| OBS | `python scripts/validate_obs_track_b_synchronization.py` | PASS |
| OBS | `python scripts/validate_obs_human_review_packet.py` | PASS |
| Track B | Track B validators through pack export | PASS |
| Generated artifacts | `python scripts/check_generated_artifact_drift.py --json` | PASS |
| Tests | `python -m unittest discover -s tests -t .` | PASS |
| AIDE | AIDE Lite doctor/validate/test/selftest/eval/review-pack/adapter | PASS |
| AIDE | AIDE Lite verify | WARN, zero errors |
