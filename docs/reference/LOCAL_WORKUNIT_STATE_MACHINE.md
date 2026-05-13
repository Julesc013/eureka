# Local WorkUnit State Machine

## Types

- `search_need`
- `source_probe`
- `evidence_review`
- `index_rebuild`
- `regression_test`
- `extraction_task`
- `agent_task`

These are queue record types only. They do not enable execution in LOCAL-07.

## States

- `queued`
- `running`
- `paused`
- `blocked`
- `complete`
- `failed`
- `cancelled`

## Transitions

Allowed transitions:

- `queued` to `running`, `paused`, `blocked`, or `cancelled`
- `running` to `paused`, `complete`, `failed`, `blocked`, or `cancelled`
- `paused` to `queued` or `cancelled`
- `blocked` to `queued` or `cancelled`
- `failed` to `queued`
- `complete` to `complete`
- `cancelled` to `cancelled`

Invalid transitions fail closed and leave the current record state unchanged. Terminal repeats are idempotent where practical.

Every create and accepted transition is recorded in append-only transition history.
