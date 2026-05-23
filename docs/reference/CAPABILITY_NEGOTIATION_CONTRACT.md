# Capability Negotiation Contract

`contracts/representation/capability_negotiation.v0.json` defines how Eureka
chooses a representation profile for a request or future client capability
manifest. It is selection policy only.

Inventory:

- `control/inventory/publication/capability_negotiation_policy.json`

## Selection Order

The required order is:

1. explicit URL parameter
2. explicit user/account/device preference, future only
3. native app or relay capability manifest, future only
4. host profile
5. `Accept` header
6. client hints, future and optional
7. conservative user-agent inference
8. safest default

Explicit selectors can ask for a representation. They cannot activate runtime
behavior or change what a route means.

## Allowed Selector Fields

The v0 selector vocabulary is:

- `format`
- `profile`
- `skin`
- `density`
- `client`
- `caps`

`skin` and `density` are presentation hints only. They must not alter source,
evidence, status, rights, risk, limitation, route, or action meaning.

## Blocked Behavior

Negotiation must not permit:

- route identity changes
- source, evidence, or status meaning changes
- hiding risk, rights, or limitations
- auth on public-read-only legacy hosts
- automatic live-source behavior
- automatic downloads, installers, or execution
- private data exposure
- API token exposure

## Future-Only Inputs

User/account/device preferences and native/relay capability manifests are
future-only in v0. They are recorded so future clients can be governed by the
same order, not because accounts, native apps, relay runtime, private device
state, cookies, or telemetry exist now.

## No-Goals

This contract does not change runtime behavior, public routes, hosted behavior,
static artifacts, live probes, source connectors, downloads, uploads, accounts,
telemetry, native projects, relay runtime, snapshot runtime, or product search
behavior.
