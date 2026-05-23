# Route/View/Representation Matrix

`contracts/representation/route_view_representation_matrix.v0.json` defines
the Track A matrix that binds Eureka route families to canonical view-model
families, allowed representation profiles, host-profile exposure, semantic
parity policy, and current/future status.

Inventory:

- `control/inventory/publication/route_view_representation_matrix.json`

## Doctrine

A Eureka route has one meaning. A Eureka page has one canonical view-model
family. A host/profile may choose a default representation. A renderer may
simplify presentation. A renderer must not change source, evidence, status,
rights, risk, limitation, action, absence, candidate, or route meaning.

## What The Matrix Defines

Each route family records:

- canonical path pattern
- current route status
- canonical view family
- allowed host profiles
- allowed representation profiles
- default representation profile
- required semantic parity policy
- current artifacts and future artifacts
- deferred behavior and no-goals

The matrix also records view families, representation bindings, host-profile
bindings, semantic parity bindings, status vocabulary, default fallbacks,
forbidden route splits, and the public-alpha gating policy.

## Status Vocabulary

Route status uses the bounded vocabulary:

- `implemented_static`
- `implemented_local_runtime`
- `contract_only`
- `planned`
- `future`
- `deferred`
- `blocked`
- `operator_gated`
- `human_operated`
- `approval_gated`

Static, lite, text, files, data, and demo route families may be marked
`implemented_static` only where committed static artifacts already support that
classification. Local public search routes may be marked
`implemented_local_runtime` only for local/prototype runtime behavior already
documented by public-search inventories. Hosted public alpha remains Track E
and operator-gated.

## Route Identity

Profiles choose representation. They do not create route meaning splits.

The matrix explicitly forbids:

- `/modern/search`
- `/old/search`
- `/mobile/search`
- `/retro/search`
- `/desktop/search`
- `/legacy/object`
- `/classic/object`

Use host/profile/capability negotiation instead of those route identities.

## Public Alpha Gate

Early public-alpha-shaped work means local, static, staging, or localhost
rehearsal evidence. Actual hosted public alpha is Track E only. The matrix does
not imply that dynamic hosted search is active.

## Semantic Parity Binding

Every route family binds to an existing semantic parity policy from
`control/inventory/publication/semantic_renderer_parity_policy.json`.

Where Track A-02 did not define a route-specific policy, the matrix uses an
explicit inherited binding to the closest conservative A-02 policy and records
that a later view-model task may split it into a more specific parity policy.
This keeps A-03 narrow and avoids rewriting the semantic parity contract in the
matrix milestone.

## No-Goals

This matrix does not add public routes, route handlers, renderer runtime,
view-model runtime, hosted backend behavior, deployment, DNS/CNAME/custom
domains, live probes, source connectors, generated site artifacts, downloads,
installers, execution, uploads, accounts, telemetry, native projects, relay
runtime, snapshot runtime, master-index mutation, or public search semantic
changes.
