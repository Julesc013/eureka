# INSTANCE-LAYOUT-CLEAN-MACHINE-FIX-01 Audit

This audit records the repair for the two INSTANCE-LAYOUT-caused LOCAL-13 clean-machine failures.

The repair is intentionally narrow:

- normal operator defaults remain `../instances/default`
- explicit legacy sibling `../eureka-instance` remains supported
- normal repo-nested instance roots remain rejected
- the LOCAL-13 non-git temp-copy harness may use `eureka-clean-machine-*/checkout/eureka-instance`

No operator instance was moved, copied, deleted, or mutated.
