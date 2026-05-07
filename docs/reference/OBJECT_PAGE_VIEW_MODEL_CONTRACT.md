# ObjectPage View Model Contract

`contracts/views/object_page.v0.json` defines the first canonical public
ObjectPage view model for Track A. It is a meaning layer for future Eureka
object/product pages, not a renderer implementation, route activation, hosted
backend, or runtime object-page feature.

Inventory:

- `control/inventory/publication/object_page_view_model_policy.json`

Examples:

- `examples/view_models/object_page/minimal_object_page_v0.json`
- `examples/view_models/object_page/software_object_page_v0.json`
- `examples/view_models/object_page/member_object_page_v0.json`
- `examples/view_models/object_page/candidate_object_page_v0.json`

## Doctrine

A Eureka object has one identity. An ObjectPage has one canonical view model.
Renderers may simplify layout, density, media, styling, and interactivity. They
must not change object identity, object state, source posture, evidence posture,
representation/member posture, compatibility posture, rights/risk posture,
allowed actions, blocked actions, limitations, gaps, review state, provenance,
canonical links, or stable IDs.

## Relationship To Existing Contracts

ObjectPageView is narrower than the older object page contract in
`docs/reference/OBJECT_PAGE_CONTRACT.md`. That historical contract remains an
evidence-first page contract. Track A-05 adds the renderer-facing canonical view
model that later standard, lite, text, file, API-adjacent, snapshot, relay,
terminal, print, and native-card projections must preserve.

ObjectPageView also relates to:

- `contracts/api/search_result_card.v0.json` for future result-card references.
- `contracts/views/search_page.v0.json` for search-to-object navigation.
- `control/inventory/publication/route_view_representation_matrix.json` for the
  `object_page_future` route/view binding.
- `control/inventory/publication/semantic_renderer_parity_policy.json` for
  `object_page_parity_v0`.

This contract does not mutate public search, result cards, source/evidence
records, public indexes, local indexes, generated site artifacts, or master
indexes.

## Required Meaning

Every ObjectPageView record carries:

- canonical object identity
- object type and known/provisional/candidate/member/source-observed state
- partial or unknown version/state fields represented honestly
- representation, file, member, manifest, and future snapshot summaries
- source, evidence, provenance, and conflict posture
- compatibility, rights, and risk posture
- allowed and blocked actions
- related records and future references
- candidate/review state
- absence/gap limitations
- representation hints that preserve semantic meaning

## Smallest Actionable Unit

ObjectPageView supports member and inner-object pages. A useful member inside a
container can be the page target, but parent container lineage must remain
visible. Member records must not be detached from source, evidence, provenance,
or representation context.

## Blocked Claims

Current examples must keep these runtime posture flags false:

- `hosted_backend_claimed`
- `live_probes_enabled`
- `downloads_enabled`
- `uploads_enabled`
- `accounts_enabled`
- `telemetry_enabled`

They must also keep these claim booleans false:

- `rights_clearance_claimed`
- `malware_safety_claimed`
- `verified_installability_claimed`
- `authorized_downloads_claimed`
- `safe_execution_claimed`

Unknown rights, unknown risk, unknown compatibility, and missing evidence are
valid public answers. They must not be filled with invented certainty.

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

Hints are renderer guidance only. They must not alter underlying object meaning
or hide source, evidence, risk, rights, limitations, gaps, parent lineage, or
blocked action posture.

## No-Goals

This contract does not add product runtime behavior, object-page runtime,
public route activation, hosted backend behavior, deployment, DNS/CNAME/custom
domains, live probes, source connectors, network/model/provider calls,
downloads, installers, execution, uploads, accounts, telemetry, native
projects, generated site artifact changes, rights-clearance claims,
malware-safety claims, verified-installability claims, master-index mutation, or
public search semantic changes.

## Validation

Run:

- `python scripts/validate_object_page_view_model.py`
- `python -m unittest tests.contracts.test_object_page_view_model`

The validator checks schema and policy shape, representation and semantic parity
references, object state/type vocabulary, route matrix binding, source/evidence
truth boundaries, member parent lineage, runtime posture flags, rights/risk and
installability claims, blocked actions, and compact examples.
