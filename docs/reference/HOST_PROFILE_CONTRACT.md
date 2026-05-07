# Host Profile Contract

`contracts/representations/host_profile.v0.json` defines a host/profile as a
representation selector. A host profile may choose defaults and allowed
representation profiles, but it does not define a separate Eureka product and
does not create runtime behavior.

Inventory:

- `control/inventory/publication/host_profiles.json`

## Doctrine

Eureka has one resolver truth, one route meaning, and many compatible
projections. Host aliases can select a default projection for canonical web,
legacy web, API-like output, static files, status pages, future nodes/tasks,
and future local relay clients. They must not change source, evidence, status,
rights, risk, limitation, or action meaning.

## Required Shape

Each host profile records:

- `schema_version`
- `host_profile_id`
- `host_role`
- `label`
- `description`
- `canonical`
- `public_read_only`
- `auth_allowed`
- `default_representation_profile`
- `allowed_representation_profiles`
- `allowed_route_families`
- `forbidden_route_families`
- `https_required`
- `http_allowed`
- `legacy_http_compatible`
- `hsts_allowed`
- `include_subdomains_hsts_allowed`
- `cookie_allowed`
- `credential_allowed`
- `write_actions_allowed`
- `private_data_allowed`
- `api_tokens_allowed`
- `unsafe_actions_allowed`
- `route_identity_policy`
- `no_product_runtime_behavior`
- `notes`

The default representation profile must exist in the representation inventory
and must also appear in `allowed_representation_profiles`.

## Legacy And HTTP-Compatible Hosts

Old-client and HTTP-compatible host profiles are public-read-only only.

They must allow none of the following:

- auth
- cookies
- credentials
- account actions
- writes
- private data
- API tokens
- unsafe actions
- downloads or installers
- live probes or live source behavior

This rule applies to `old_legacy_read_only`, `files_static`, `status_static`,
`localhost_relay_future`, and any later profile with `http_allowed: true` or
`legacy_http_compatible: true`.

## No-Goals

This contract does not change runtime behavior, hosted behavior, public routes,
DNS, CNAME, custom domains, source connectors, live probes, public search
behavior, generated site artifacts, native projects, downloads, uploads,
accounts, telemetry, or product search semantics.
