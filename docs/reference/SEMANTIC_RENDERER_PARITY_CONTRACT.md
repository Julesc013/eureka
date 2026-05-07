# Semantic Renderer Parity Contract

`contracts/representations/semantic_renderer_parity.v0.json` defines the
Track A policy record that every Eureka renderer/projection must satisfy before
future view-model or renderer work can widen.

Inventory:

- `control/inventory/publication/semantic_renderer_parity_policy.json`

## Doctrine

Eureka has one resolver truth, one route meaning, one canonical view model, and
many compatible projections. Renderers may simplify layout, density, media,
interactivity, styling, and presentation. They must not change or hide source,
evidence, status, rights, risk, limitation, action, absence, candidate, or
canonical identity meaning.

Plain text, lite HTML, file-tree, snapshot, relay, terminal, print, and future
native-card projections are first-class semantic projections. They are not
disposable fallbacks.

## Required Shape

Each parity policy records:

- `schema_version`
- `parity_policy_id`
- `label`
- `description`
- `applies_to_view_family`
- `applies_to_route_family`
- `source_contracts`
- `allowed_representation_profiles`
- `required_semantic_fields`
- `required_action_fields`
- `required_status_fields`
- `required_warning_fields`
- `required_link_fields`
- `required_absence_fields`
- `allowed_degradations`
- `forbidden_omissions`
- `forbidden_transformations`
- `representation_specific_requirements`
- `parity_check_strategy`
- `review_required`
- boundary booleans proving no product behavior was enabled
- `notes`

## Semantic Categories

The standard semantic categories are:

- `identity`
- `canonical_id`
- `canonical_route`
- `title_or_label`
- `object_type`
- `result_state`
- `source_posture`
- `evidence_summary`
- `evidence_links`
- `compatibility_summary`
- `rights_posture`
- `risk_posture`
- `allowed_actions`
- `blocked_actions`
- `limitations`
- `gaps`
- `absence_scope`
- `confidence_or_uncertainty`
- `candidate_review_state`
- `provenance_or_lineage`
- `generated_or_observed_status`
- `last_updated_or_observed_when_available`

Not every route or view family must contain every category. Every parity policy
must say which categories are mandatory for that family.

## Allowed Degradation

Allowed degradation changes presentation only, for example:

- rich graph to edge list
- interactive compare to numbered comparison table
- visual badges to text labels
- expandable evidence panel to evidence link list
- download queue to manifest link
- inline preview to metadata and external/open action
- account watch button to unavailable/read-only notice
- modern card layout to plain table
- CSS styling to plain labels
- images or icons to alt text or omitted decorative icons

## Forbidden Omissions

Renderers must not:

- hide executable risk
- hide rights uncertainty
- hide source uncertainty
- hide candidate or provisional status
- hide blocked actions
- hide known absence scope
- hide unresolved gaps
- hide conflicting evidence
- convert candidate into verified result
- convert source observation into accepted truth
- convert AI draft into evidence truth
- remove canonical object, source, or evidence links when links are supported
- change route identity based on profile
- imply hosted/live behavior where unavailable
- imply downloads, installers, uploads, accounts, telemetry, or execution where
  unavailable

## Representation Requirements

The policy inventory defines requirements for:

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

Text projections must preserve semantic labels as plain text and include
canonical IDs plus limitations. File-tree projections must preserve manifest,
checksum, and source summaries while avoiding live API or executable hosting
claims. API JSON must preserve machine-readable identity, status, evidence,
action, and limitation fields without inventing omitted values. Future native
cards must preserve risk, rights, source, evidence, and action posture even
when rich page content is reduced to navigation and summary fields.

## No-Goals

This contract does not add renderer runtime, view-model runtime, public routes,
hosted backend behavior, live probes, source connectors, generated site
artifacts, downloads, installers, execution, uploads, accounts, telemetry,
native projects, relay runtime, snapshot runtime, or master-index mutation.
