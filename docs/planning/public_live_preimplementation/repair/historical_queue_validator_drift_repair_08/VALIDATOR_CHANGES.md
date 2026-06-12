# Validator Changes

Changed files:

```text
tools/generators/hunt_queue_progress.py
scripts/validate_public_alpha_launch_defer.py
scripts/validate_dev_to_main_promotion_03.py
scripts/validate_dev_to_main_promotion_04.py
tests/operations/test_hunt_main_promotion_gates.py
tests/operations/test_public_alpha_launch_defer.py
tests/operations/test_dev_to_main_promotion_03.py
tests/operations/test_dev_to_main_promotion_04.py
```

Repair shape:

- Add explicit IA metadata provider smoke successor recognition.
- Keep numbered repair/rerun/ingest prefixes recognized as governed successor states.
- Keep evidence and hardware waiting states recognized as blocked successor states.
- Add regression tests for current advanced states.
- Add regression tests that public alpha launch/readiness and dev-to-main promotion tasks remain rejected without their dedicated gates.

No broad wildcard successor acceptance was added.

