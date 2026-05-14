# Command Summary

HUNT-03 adds local state commands for Search Hunt Sessions:

- pause
- resume
- cancel
- block
- wait_for_user
- wait_for_policy
- complete
- fail

Commands are applied through the governed Search Hunt state machine, require an operator token for mutations, and record command history. `block` and `fail` require a reason.
