# Validation Matrix

| validation_class | status | command | notes |
| --- | --- | --- | --- |
| git_state | pass | git status --short --branch |  |
| AIDE doctor | pass | py -3 .aide/scripts/aide_lite.py doctor |  |
| AIDE validate | pass | py -3 .aide/scripts/aide_lite.py validate |  |
| AIDE test | pass | py -3 .aide/scripts/aide_lite.py test |  |
| AIDE selftest | pass | py -3 .aide/scripts/aide_lite.py selftest |  |
| AIDE verify | pass | py -3 .aide/scripts/aide_lite.py verify |  |
| AIDE review-pack | pass | py -3 .aide/scripts/aide_lite.py review-pack |  |
| AIDE eval run | pass | py -3 .aide/scripts/aide_lite.py eval run | 136/136 golden tasks pass |
| AIDE commit check | pass | py -3 .aide/scripts/aide_lite.py commit check --latest |  |
| HUNT validators | pass | HUNT validator sweep |  |
| LOCAL dependency validators | pass | LOCAL dependency validator sweep |  |
| HUNT workflow smoke | pass | python scripts/eureka_hunt_workflow_smoke.py --instance ./eureka-instance --operator-token local-dev-token --query sampleproject --json |  |
| HUNT API smoke | pass | python scripts/eureka_hunt_api_smoke.py --base-url http://127.0.0.1:8765 --json |  |
| HUNT workbench smoke | pass | python scripts/eureka_hunt_workbench_smoke.py --base-url http://127.0.0.1:8765 --instance ./eureka-instance --operator-token local-dev-token --json |  |
| HUNT replay demo | pass | python scripts/demo_hunt_replay.py --instance ./eureka-instance --operator-token local-dev-token --query sampleproject --json |  |
| HUNT AI escalation disabled-boundary demo | pass | python scripts/demo_ai_escalation_gate.py --instance ./eureka-instance --operator-token local-dev-token --query sampleproject --json |  |
| full unittest discovery | pass | python -m unittest discover -s tests -t . | 4520 tests passed in warning-zero sweep; rerun for perfect closeout |
| generated artifact cleanliness | pass | python scripts/check_generated_artifact_cleanliness.py --check --json |  |
| architecture boundaries | pass | python scripts/check_architecture_boundaries.py |  |
| runtime leakage | pass | python scripts/audit_runtime_architecture_leakage.py --check --json; python scripts/validate_runtime_architecture_leakage.py | zero new unallowlisted findings; known allowlisted findings remain tracked |
| report-size checks | pass | python scripts/validate_aide_report_sizes.py --json |  |
| secret/raw prompt/raw response checks | pass | py -3 .aide/scripts/aide_lite.py verify | no tracked secrets/raw prompt/raw response storage found by AIDE checks |
