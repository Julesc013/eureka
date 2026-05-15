# Side Effect Boundary

HUNT-04 may write an exhaustion report row and append command history for that report generation. It does not create WorkUnits, execute source probes, call providers, mutate review decisions, rebuild indexes, or mutate public/master indexes.
