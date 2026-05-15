# Validation

Primary validator: `python scripts/validate_search_hunt_workbench_integration.py`.

Focused smoke scripts:

- `python scripts/eureka_hunt_workflow_smoke.py --instance <path> --operator-token <token> --json`
- `python scripts/eureka_hunt_workbench_smoke.py --base-url http://127.0.0.1:<port> --json`
- `python scripts/eureka_hunt_api_smoke.py --base-url http://127.0.0.1:<port> --json`
