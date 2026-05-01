# Integration Boundaries

P62 does not wire search need creation into the public search runtime. It does
not add a database, runtime store, telemetry, public query logging, result cache
mutation, miss ledger mutation, probe enqueueing, candidate-index mutation,
local-index mutation, or master-index mutation.

Future integration belongs after query privacy and poisoning policy, probe
queue, candidate index, and promotion policy are governed.
