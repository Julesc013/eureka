# Search Hunt Command Boundaries

HUNT-03 is command recording and local state control only.

Allowed:

- mutate Search Hunt session state through the governed state machine
- append command history
- record or deactivate steering preferences
- show operator controls in the local workbench when the service is opened with operator-capable local runtime state

Forbidden:

- WorkUnit creation
- source probe execution
- extraction execution
- external network search
- crawling or scraping
- AI/model/provider calls
- review decision mutation
- public index mutation
- master index mutation
- LAN command mutation
- deployment
- production readiness claims
- public launch readiness claims

HUNT-04 is the next step because commands need a structured exhaustion report before HUNT creates SearchNeeds or WorkUnits.
