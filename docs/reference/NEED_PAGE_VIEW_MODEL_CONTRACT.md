# NeedPage View Model Contract

`contracts/views/need_page.v0.json` defines the first canonical public
NeedPage view model for Track A. A need is a reusable unresolved-search object,
not a failed page and not telemetry. It can carry scoped absence, near misses,
source gaps, candidate leads, aggregate demand posture, and future safe work
without changing public search runtime behavior.

Inventory:

- `control/inventory/publication/need_page_view_model_policy.json`

Examples:

- `examples/view_models/need_page/minimal_need_page_v0.json`
- `examples/view_models/need_page/known_absence_need_page_v0.json`
- `examples/view_models/need_page/source_gap_need_page_v0.json`
- `examples/view_models/need_page/work_unit_future_need_page_v0.json`

## Doctrine

A Eureka need preserves unresolved demand and absence scope as first-class
meaning. Renderers may simplify layout, density, styling, or interactivity, but
must not change need identity, query intent, aggregate demand posture, absence
scope, source gaps, candidate state, evidence posture, rights/risk/privacy
caveats, allowed actions, blocked actions, limitations, or unresolved gaps.

## Relationship To Existing Contracts

NeedPageView references these governance inputs:

- `contracts/query/search_need_record.v0.json`
- `contracts/query/search_miss_ledger_entry.v0.json`
- `contracts/query/known_absence_page.v0.json`
- `contracts/query/demand_signal.v0.json`
- `docs/reference/DEMAND_DASHBOARD_CONTRACT.md`
- `control/inventory/publication/route_view_representation_matrix.json`
- `control/inventory/publication/semantic_renderer_parity_policy.json`

This contract does not create a need store, demand dashboard runtime, probe
queue runtime, node task, account watch, public submission system, telemetry,
raw query retention, source sync, connector, public route, or master-index
mutation.

## Required Meaning

Every NeedPageView record carries:

- canonical need identity and route
- query and interpreted intent posture
- aggregate-only demand summary
- privacy and poisoning-guard posture
- scoped absence summary
- searched and not-searched scope
- sources checked and not checked
- source gaps, capability gaps, policy blocks, near matches, and candidates
- evidence posture and limitations
- future work-unit and contribution summaries
- rights, risk, allowed actions, blocked actions, warnings, and notes

## Absence Scope

NeedPageView must distinguish no verified result, candidate exists, near miss
exists, source gap exists, capability gap exists, policy blocked, and not
searched yet. Absence is scoped to checked evidence and must not become
exhaustive global proof.

## Demand And Privacy

Demand fields are aggregate and privacy-filtered. Current examples must not
claim telemetry, account identity, raw user tracking, public raw-query storage,
or demand-derived object truth.

## Blocked Claims

Current examples keep hosted backend, live probe, source sync, download, upload,
account, telemetry, node task, public submission, and master-index mutation
behavior unavailable. Future work-unit, evidence submission, source suggestion,
watch, and node-task actions are labels for future governance only.

## Representation Hints

The first policy covers `standard_html`, `lite_html`, `html32`, `text`,
`file_tree`, `api_json`, `manifest_json`, `snapshot_future`, `relay_future`,
`terminal_future`, `native_card_future`, and `print`.

Hints are renderer guidance only. They must not alter need meaning or hide
absence scope, demand privacy posture, gaps, candidates, evidence caveats, or
blocked actions.

## Validation

Run:

- `python scripts/validate_need_candidate_page_view_models.py`
- `python -m unittest tests.contracts.test_need_candidate_page_view_models`
