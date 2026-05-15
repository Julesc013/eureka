# SearchNeed State Machine

States:

- `proposed`
- `open`
- `waiting_for_user`
- `waiting_for_policy`
- `blocked`
- `satisfied_locally`
- `superseded`
- `cancelled`

Invalid transitions fail closed. Terminal states are idempotent only to themselves. Every state update records transition history.
