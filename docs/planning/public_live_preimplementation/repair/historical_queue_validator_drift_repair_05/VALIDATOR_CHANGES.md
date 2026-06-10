# Validator Changes

## HUNT Queue Progress

`tools/generators/hunt_queue_progress.py` now accepts the governed external evidence, external discovery, and hardware-detail waiting states as post-HUNT advanced queue posture.

## LOCAL Queue Progress

`tools/generators/local_queue_progress.py` now accepts the same waiting states as later control or handoff posture for completed LOCAL validators.

## Public Alpha Defer

`scripts/validate_public_alpha_launch_defer.py` now accepts the same waiting states as later blocked repair/readiness posture after `PUBLIC-ALPHA-LAUNCH-DEFER-00`.

## Dev To Main Promotion 03/04

`scripts/validate_dev_to_main_promotion_03.py` and `scripts/validate_dev_to_main_promotion_04.py` now treat the waiting states as valid post-promotion successor posture for historical validation.

## Focused Tests

Focused helper tests were added for:

```text
post-HUNT external artifact evidence wait state
LOCAL external artifact evidence wait state
```

