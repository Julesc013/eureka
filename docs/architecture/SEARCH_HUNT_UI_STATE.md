# Search Hunt UI State

HUNT-02 adds read-only Search Hunt visibility to the Local Appliance workbench.

The UI shows persisted Search Hunt Sessions from the explicit local instance. It does not create hunts, change hunt state, create WorkUnits, run source probes, call model providers, mutate review decisions, rebuild indexes, or deploy.

## Pages

- `/hunts` lists local Search Hunt Sessions.
- `/hunt/<hunt_id>` shows one session, its checked layers, deferred layers, summaries, limitations, warnings, and transition history.
- Missing hunt IDs render a not-found page and are not created implicitly.

## Boundary

A Search Hunt Session is investigation state only. Reviewed local index results and local/current-index absence are displayed separately, and unchecked layers remain visible as deferred work.

## HUNT-03 Controls

When the local service is opened with operator-capable localhost state, the hunt detail page also shows token-gated state controls, steering preference forms, command history, and active/inactive steering preferences. These controls submit only to localhost command routes and remain unavailable to LAN clients.

## HUNT-04 Exhaustion

The hunt detail page now shows the latest exhaustion report, checked layers, deferred layers, blocked-by-policy entries, future action categories, and non-claims. Report generation is token-gated and localhost-only; LAN clients can only read existing report state.
