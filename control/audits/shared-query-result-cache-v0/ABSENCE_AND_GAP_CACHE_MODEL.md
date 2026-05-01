# Absence And Gap Cache Model

The absence model supports:

- `not_absent`
- `no_verified_result`
- `scoped_absence`
- `known_unresolved_need_future`
- `blocked_by_policy`

Cached absence is scoped to checked indexes, sources, and snapshots. It is not
a claim that an object is absent outside the checked scope. Future miss ledger
or search need records may reuse the summary only after privacy and poisoning
review.
