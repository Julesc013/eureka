# SearchPage View Model Contract

`contracts/views/search_page.v0.json` defines the first canonical public
SearchPage view model for Track A. It is a meaning layer for Eureka search
pages, not a renderer implementation and not a runtime change.

Inventory:

- `control/inventory/publication/search_page_view_model_policy.json`

Examples:

- `examples/view_models/search_page/minimal_search_page_v0.json`
- `examples/view_models/search_page/empty_search_page_v0.json`
- `examples/view_models/search_page/absence_search_page_v0.json`
- `examples/view_models/search_page/result_card_search_page_v0.json`

## Doctrine

A search route has one meaning. A SearchPage has one canonical view model.
Renderers may simplify layout, media, density, styling, or interactivity. They
must not change query identity, source posture, evidence posture, result state,
rights/risk posture, allowed and blocked actions, limitations, gaps, absence
scope, canonical links, or stable IDs.

## Relationship To Existing Search Contracts

SearchPageView sits above the public search API and result-card contracts:

- `contracts/api/search_response.v0.json` governs the API response envelope.
- `contracts/api/search_result_card.v0.json` governs public result cards.
- SearchPageView may reference or embed compact result-card-shaped records, but
  it must not contradict the result-card contract.

This contract does not make `/search` or `/api/v1/search` hosted. Existing
local/prototype and static search behavior remains unchanged.

## Required Meaning

Every SearchPageView record carries:

- route and view identity
- page and search status
- search mode and public runtime posture
- query identity and privacy posture
- interpreted intent when available
- result summary, result records, and result sections
- source and evidence summaries
- absence details when applicable
- limitations, warnings, allowed actions, and blocked actions
- representation hints that preserve semantic meaning

Current static and local examples must explicitly keep these posture flags
false:

- `hosted_backend_claimed`
- `live_probes_enabled`
- `downloads_enabled`
- `uploads_enabled`
- `accounts_enabled`
- `telemetry_enabled`

## Search Modes

The bounded search-mode vocabulary is:

- `local_index_only`
- `static_handoff`
- `static_demo`
- `fixture_backed`
- `future_hosted`
- `future_source_cache`
- `future_live_probe_disabled`
- `future_node_task`

Future modes are contract vocabulary only unless a later reviewed milestone
implements them.

## Result Sections

Allowed section names are:

- `verified_or_reviewed_results`
- `provisional_candidates`
- `near_misses`
- `known_absence`
- `source_leads`
- `policy_blocked`
- `private_local_only_future`

Candidate or provisional records must remain labeled as candidates or
provisional. They must not be rendered as verified truth.

## Absence

SearchPageView supports useful no-result and weak-result cases. An absence
record may describe searched scope, checked and unchecked sources, near matches,
known gaps, and safe next actions. It must not imply exhaustive global search
unless that is supported by explicit evidence in a later contract.

## Representation Hints

The first policy covers:

- `standard_html`
- `lite_html`
- `html32`
- `text`
- `file_tree`
- `api_json`
- `snapshot_future`
- `relay_future`
- `terminal_future`
- `native_card_future`

Hints are renderer guidance only. They must not alter the underlying search
meaning or hide safety, rights, risk, source, evidence, limitation, gap, or
absence posture.

## No-Goals

This contract does not add product runtime behavior, public route activation,
hosted backend behavior, deployment, DNS/CNAME/custom domains, live probes,
source connectors, network/model/provider calls, downloads, installers,
execution, uploads, accounts, telemetry, native projects, generated site
artifact changes, master-index mutation, or public search semantic changes.

## Validation

Run:

- `python scripts/validate_search_page_view_model.py`
- `python -m unittest tests.contracts.test_search_page_view_model`

The validator checks schema and inventory shape, representation and semantic
parity references, section/action/search-mode vocabulary, public runtime posture
flags, candidate/provisional status, absence scope, and compact examples.
