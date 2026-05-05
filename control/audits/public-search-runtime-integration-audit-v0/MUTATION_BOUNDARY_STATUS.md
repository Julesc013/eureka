# Mutation Boundary Status

Public search currently must not mutate:

- source cache
- evidence ledger
- result cache
- miss ledger
- search need records
- probe queue
- candidate index
- public index
- local index
- runtime index
- master index

No mutation integration was found. If any future public-search path writes to one
of these stores without an explicit reviewed milestone, classify it as
`unexpected_integration` and a blocker.

