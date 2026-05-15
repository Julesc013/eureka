# Hunt-to-WorkUnit Boundaries

HUNT-06 permits local WorkUnit record creation from SearchNeeds.

It forbids:

- WorkUnit execution
- source probe execution
- extraction
- model/provider calls
- external network use
- review decision mutation
- reviewed public index mutation
- master index mutation
- deployment
- production readiness claims
- public launch readiness claims

Policy-gated WorkUnits must remain blocked until a later explicit gate enables execution.
