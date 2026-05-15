# Hunt Replay Runbook

1. Initialize a local instance and set an operator token.
2. Create or select a local Search Hunt workflow.
3. Run `python scripts/eureka_hunt_replay.py --instance <path> --hunt-id <hunt_id> plan --json`.
4. Run `python scripts/eureka_hunt_replay.py --instance <path> --hunt-id <hunt_id> --operator-token <token> replay-local --json`.
5. Run `python scripts/eureka_hunt_replay.py --instance <path> --hunt-id <hunt_id> verify-existing --json`.
6. Inspect `/hunt/<hunt_id>/replay` or `/api/v1/hunt/<hunt_id>/replay`.

Replay-local should be used on explicit local instances. For validator isolation, use disposable temp instances.
