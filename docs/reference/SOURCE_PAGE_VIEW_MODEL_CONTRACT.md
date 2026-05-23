# SourcePage View Model Contract

`contracts/view/pages/source_page.v0.json` defines the first canonical public
SourcePage view model for Track A. It is a meaning layer for source list,
source detail, and source coverage pages, not a renderer implementation, route
activation, hosted backend, source connector, source sync runtime, crawler,
scraper, mirror, or source API proxy.

Inventory:

- `control/inventory/publication/source_page_view_model_policy.json`

Examples:

- `examples/view_models/source_page/minimal_source_page_v0.json`
- `examples/view_models/source_page/recorded_fixture_source_page_v0.json`
- `examples/view_models/source_page/placeholder_source_page_v0.json`
- `examples/view_models/source_page/source_gap_page_v0.json`

## Doctrine

A Eureka source has one identity. A SourcePage has one canonical view model.
Renderers may simplify layout, density, media, styling, and interactivity. They
must not change source identity, source type, authority posture, coverage,
policy gates, connector status, cache posture, evidence ledger posture, rights,
risk, privacy, limitations, gaps, review state, allowed actions, blocked
actions, canonical links, or stable IDs.

## Relationship To Existing Contracts

SourcePageView is narrower than the older evidence-first source page contract
in `docs/reference/SOURCE_PAGE_CONTRACT.md`. That historical contract remains
a broader planning and page-contract reference. Track A-06 adds the
renderer-facing canonical view model that standard, lite, HTML 3.2-ish, text,
file-tree summary, API-adjacent, manifest, snapshot, relay, terminal, print,
and native-card projections must preserve.

SourcePageView also relates to:

- `contracts/source/registry/` for governed source identity and capability
  vocabulary.
- `docs/reference/SOURCE_PACK_CONTRACT.md` for future source-pack references.
- `docs/reference/EVIDENCE_PACK_CONTRACT.md` for future evidence-pack
  references.
- `docs/reference/SOURCE_CACHE_CONTRACT.md` and
  `docs/reference/EVIDENCE_LEDGER_CONTRACT.md` for source-cache and evidence
  ledger posture.
- `control/inventory/publication/route_view_representation_matrix.json` for the
  `source_detail` route/view binding.
- `control/inventory/publication/semantic_renderer_parity_policy.json` for
  `source_page_parity_v0`.

This contract does not mutate source registry records, source packs, evidence
packs, source cache records, evidence ledger records, public indexes, local
indexes, generated site artifacts, source connectors, source sync workers, or
master indexes.

## Required Meaning

Every SourcePageView record carries:

- canonical source identity and public-safe source references
- source family, kind, scope, status, and authority posture
- source policy and access gates
- source capability and coverage posture
- connector mode, implementation status, and disabled live-probe/source-sync
  status
- source cache and evidence ledger posture
- observed-record status and example record refs
- related source/evidence packs and related objects
- known limitations and gaps
- rights, risk, and privacy posture
- allowed and blocked actions
- candidate/review/placeholder state
- representation hints that preserve semantic meaning

## Access And Connector Boundaries

SourcePageView distinguishes fixture, recorded fixture, placeholder, future,
manual-only, approval-gated, operator-gated, policy-blocked, and deprecated
sources. Placeholder, future, manual-only, and recorded fixture sources must
not be represented as live connectors.

Current examples keep these connector and product-boundary flags false:

- `hosted_backend_claimed`
- `hosted_connector_enabled`
- `live_probes_enabled`
- `source_sync_runtime_enabled`
- `downloads_enabled`
- `uploads_enabled`
- `accounts_enabled`
- `telemetry_enabled`

Allowed and forbidden access modes are descriptive policy fields. They do not
authorize crawling, scraping, source sync, arbitrary URL fetch, API calls,
mirroring, or downloads.

## Truth Boundaries

SourcePageView must not convert:

- source cache records into accepted truth
- source observations into accepted truth
- evidence candidates into verified facts
- manual observation placeholders into completed external baselines
- AI drafts into evidence truth
- source policy posture into connector approval
- source pages into live source API proxies

Unknown coverage, unknown rights, unknown risk, and incomplete evidence are
valid public answers. They must not be filled with invented certainty.

## Blocked Claims

Current examples must not claim:

- rights clearance
- malware safety
- legal permission to mirror or download everything
- unrestricted crawling or scraping
- authorized bulk access
- safe execution
- account, telemetry, upload, hosted backend, live-probe, source-sync, or
  connector behavior

The corresponding blocked actions must remain visible when a capability is
unavailable.

## Representation Hints

The first policy covers:

- `standard_html`
- `lite_html`
- `html32`
- `text`
- `file_tree`
- `api_json`
- `manifest_json`
- `snapshot_future`
- `relay_future`
- `terminal_future`
- `native_card_future`
- `print`

Hints are renderer guidance only. They must not alter underlying source meaning
or hide policy gates, evidence posture, rights/risk/privacy caveats,
limitations, gaps, connector disabled status, or blocked actions.

## No-Goals

This contract does not add product runtime behavior, source-page runtime,
public route activation, hosted backend behavior, deployment, DNS/CNAME/custom
domains, live probes, source connectors, source sync runtime, network/model/
provider calls, downloads, installers, execution, uploads, accounts, telemetry,
native projects, generated site artifact changes, rights-clearance claims,
malware-safety claims, authorized-bulk-access claims, crawling/scraping claims,
master-index mutation, or public search semantic changes.

## Validation

Run:

- `python scripts/validate_source_page_view_model.py`
- `python -m unittest tests.contracts.test_source_page_view_model`

The validator checks schema and policy shape, representation and semantic parity
references, source status/kind vocabulary, connector and access mode
vocabulary, route matrix binding, truth boundaries, placeholder and recorded
fixture live-connector boundaries, runtime posture flags, rights/risk/privacy
claims, blocked actions, and compact examples.
