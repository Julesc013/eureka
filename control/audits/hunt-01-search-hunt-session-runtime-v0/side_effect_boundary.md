# Side Effect Boundary

Allowed in HUNT-01:

- create Search Hunt Session records
- record Search Hunt state transitions
- attach reviewed-index search summaries
- attach local absence summaries

Forbidden in HUNT-01:

- WorkUnit creation
- source probes
- extraction
- model/provider calls
- review decisions
- public/master index mutation
- deployment
- production/public launch readiness claims
