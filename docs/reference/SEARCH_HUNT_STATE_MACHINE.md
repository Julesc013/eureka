# Search Hunt State Machine

Allowed states:

- `created`
- `running`
- `paused`
- `waiting_for_user`
- `waiting_for_policy`
- `blocked`
- `complete`
- `failed`
- `cancelled`

Allowed transitions:

- `created` to `running`, `paused`, `blocked`, or `cancelled`
- `running` to `paused`, `waiting_for_user`, `waiting_for_policy`, `complete`, `failed`, `blocked`, or `cancelled`
- `paused` to `running` or `cancelled`
- `waiting_for_user` to `running` or `cancelled`
- `waiting_for_policy` to `running`, `blocked`, or `cancelled`
- `blocked` to `running` or `cancelled`
- `failed` to `running`
- `complete` to `complete`
- `cancelled` to `cancelled`

Every non-idempotent transition records history in `search_hunt_transitions`. Invalid transitions are rejected.
