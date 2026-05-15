# Hunt-to-WorkUnit Runbook

Plan only:

`python scripts/eureka_need_to_workunits.py --instance ./eureka-instance --need-id <need_id> --plan-only --json`

Persist WorkUnits:

`python scripts/eureka_need_to_workunits.py --instance ./eureka-instance --need-id <need_id> --operator-token <token> --create --json`

Demo:

`python scripts/demo_hunt_to_workunits.py --instance ./eureka-instance --operator-token <token> --query "sampleproject" --json`

Validation:

`python scripts/validate_hunt_to_workunits.py`
