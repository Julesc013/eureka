# AIDE State Report

AIDE Lite is operational after SYNC-GUARD-01 and the canonical baseline merge.

## Results

- doctor: PASS
- validate: PASS
- test: PASS
- selftest: PASS
- verify: WARN, zero errors
- eval list: PASS
- eval run: PASS, 14/14
- review-pack: PASS
- adapter validate: PASS

## Remaining WARN-Only Items

- `.aide/context/context-index.json` reference warning in the latest task packet.
- Optional controller, gateway, and provider latest-status references missing from the review packet.

These are AIDE metadata warnings, not product behavior failures.

## Guard Availability

The guard is now available at:

```text
python scripts/check_git_task_state.py --mode start-task --task-id <task-id>
```

AIDE workflow prompts are available under `.aide/prompts/`.
