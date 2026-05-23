# Representation Profile Contract

`contracts/representation/representation_profile.v0.json` defines the
projection families Eureka may use when rendering the same public-safe resolver
meaning into different client shapes.

Inventory:

- `control/inventory/publication/representation_profiles.json`

## Doctrine

Representations may simplify presentation. They must not change source,
evidence, status, rights, risk, limitation, route, or action meaning.

Plain text, lite HTML, and file-tree outputs are first-class projections. They
are not disposable fallbacks and must carry the same safety and evidence meaning
as richer surfaces.

## Families

Track A-01 records these representation families:

- `standard_html`
- `lite_html`
- `html32`
- `text`
- `file_tree`
- `api_json`
- `manifest_json`
- `snapshot`
- `relay`
- `terminal`
- `native_card`
- `print`

Some families are current static seeds or existing contract outputs. Future
families remain contract-only until later Track D, Track C, or Track E work
authorizes implementation.

## Required Shape

Each representation profile records:

- `schema_version`
- `representation_profile_id`
- `representation_family`
- `label`
- `media_type`
- `route_usage`
- `javascript_required`
- `css_required`
- `cookie_required`
- `auth_allowed`
- `public_read_only`
- `max_page_weight_kb`
- `supports_forms`
- `supports_tables`
- `supports_images`
- `supports_json`
- `supports_download_manifests`
- `supports_interactive_preview`
- `renderer_status`
- `first_class_projection`
- `future_only`
- `source_evidence_status_meaning_preserved`
- `route_identity_changes_allowed`
- `semantic_requirements`
- `forbidden_omissions`
- `degradation_policy`
- `no_product_runtime_behavior`
- `notes`

`semantic_requirements` and `forbidden_omissions` are required because
representation choice is not allowed to hide risk, rights, limitation,
candidate, absence, conflict, source, evidence, or status meaning.

## No-Goals

This contract does not add renderers, public routes, hosted APIs, generated
site artifacts, live probes, source connectors, downloads, installers,
execution, uploads, accounts, telemetry, native projects, snapshot runtime, or
relay runtime.
