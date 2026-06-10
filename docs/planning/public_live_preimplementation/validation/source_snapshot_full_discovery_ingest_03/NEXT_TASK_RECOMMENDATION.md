# Next Task Recommendation

## Recommended Next Task

`HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-03`

## Why

External full-discovery rerun 03 is terminal and current to HEAD, but fails only in historical operation validators that require stale queue positions.

The repair should update validators/tests so old task validators pass when their task is completed or superseded and the live queue has moved to a later, valid task.

## Not Next

Do not launch public alpha.

Do not promote `dev -> main`.

Do not rerun full discovery until the focused validator drift repair passes local focused validation.
