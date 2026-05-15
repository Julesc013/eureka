# Hunt To SearchNeed Boundaries

HUNT-05 allows:

- creating SearchNeeds from existing hunts
- deterministic exhaustion generation when an operator token has already been accepted
- SearchNeed list/detail API and HTML views
- local SearchNeed state transitions

HUNT-05 forbids:

- WorkUnit creation
- source probe execution
- extraction execution
- AI/model/provider calls
- review decisions
- public/master index mutation
- LAN mutation
- deployment
- production or public launch readiness claims
