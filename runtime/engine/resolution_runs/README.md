# Resolution Runs

Resolution Run Model v0 adds a bounded, synchronous investigation record for
exact resolution and deterministic search.

This slice is intentionally small:

- runs are created and completed synchronously
- runs are persisted locally as JSON records
- run ids are deterministic bootstrap identifiers only and are not yet a final
  durable global run-identity contract
- the run store root is caller-supplied bootstrap state
- checked sources are derived from the bounded catalog consulted by the current
  deterministic slice and mapped through Source Registry v0 when possible

This slice does not yet provide:

- query planning
- worker queues
- async orchestration
- streaming partial results
- live source sync
- resolution memory
- database-backed persistence

The current runtime service wraps existing engine behavior rather than
re-implementing exact resolution or deterministic search.
