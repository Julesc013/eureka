# Agent Research Task Record

An agent research task record contains:

- task, hunt, need, and exhaustion IDs
- query and normalized query
- intent and destination
- checked and deferred layers
- blocked policy entries
- known candidate and absence state
- steering preferences
- allowed and blocked source families
- research goals
- forbidden actions
- candidate-only output schema
- provider and execution disabled flags
- state, warnings, and limitations

Allowed states are `drafted`, `queued_disabled`, `blocked_by_policy`, `waiting_for_provider_gate`, `cancelled`, and `superseded`.
