# Search Hunt Session Runtime

HUNT-01 adds the first durable Search Hunt Session runtime. Sessions live in the explicit Local Appliance instance as the manifest-backed `search_hunt` store at `db/search_hunt.sqlite`.

A session records local investigation state only:

- the original and normalized query
- intent and destination guesses
- reviewed-index search summary
- local absence summary
- checked and unchecked layers
- limitations, warnings, and state transition history

The runtime does not create WorkUnits, run workers, execute source probes, call model providers, mutate review decisions, mutate the reviewed public index, or mutate any master index.

## Store Boundary

`open_local_appliance(instance)` exposes `runtime.search_hunt` alongside the existing local stores. Store paths come from `config/store_manifest.json`; product code must not invent hidden paths or side databases.

## State

The state machine supports `created`, `running`, `paused`, `waiting_for_user`, `waiting_for_policy`, `blocked`, `complete`, `failed`, and `cancelled`. Invalid transitions fail closed, and terminal repeat transitions are idempotent.

## HUNT-02

Workbench visibility reads this store through the Local Appliance runtime. HUNT-02 adds list/detail pages and JSON routes only; it does not add creation, command, WorkUnit, source-probe, extraction, AI, review, or index mutation behavior.
