# State Machine

Allowed states are `created`, `running`, `paused`, `waiting_for_user`, `waiting_for_policy`, `blocked`, `complete`, `failed`, and `cancelled`.

Invalid transitions fail closed. Repeating `complete -> complete` and `cancelled -> cancelled` is idempotent.
