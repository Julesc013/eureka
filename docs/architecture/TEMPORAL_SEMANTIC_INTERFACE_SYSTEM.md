# Temporal Semantic Interface System

TSIS is the doctrine that Eureka has one semantic product language and many
negotiated representations. A route, object, evidence record, status, or action
does not become a different product because it is shown as JSON, text, HTML 3.2,
classic HTML, rich web, terminal output, native-card JSON, or an agent context
packet.

The invariant is:

```text
one object model
one route model
one evidence model
one action model
one resolution/run model
one capability model
many representations
many clients
no duplicated product logic
```

## Repo Placement

TSIS uses the existing Eureka root model:

- `contracts/` owns meaning and schemas.
- `runtime/` owns kernels and implementation when a later phase adds them.
- `runtime/surface/` is the planned Surface Kernel machinery root.
- `runtime/surface/renderers/` is the planned renderer implementation root.
- `surfaces/` owns product-facing surface packages.
- `site/`, `snapshots/`, and `examples/` hold authored/static/example payloads.
- `control/` owns governance, policies, matrices, and audit evidence.

Do not add top-level `renderers/`, `skins/`, `services/`, `apps/`, `data/`, or
`infra/` roots. Those concepts route into existing authority roots.

## Semantic Contracts

The TSIS foundation adds semantic contracts for:

- entity
- status
- badge
- navigation
- affordance
- relationship

Actions are governed through `contracts/action/action_registry.v0.json`.

Machine status IDs are canonical. Display labels can vary by renderer, but
stable state fields must not drift into synonyms such as `maybe`,
`provisional`, or `candidate-ish`.

## Representation Contracts

Representation profiles already exist under `contracts/representation/`.
TSIS adds contracts for renderer purity, skins, compatibility budgets, cache
keys, and fallback rules. These contracts make degradation testable:

- fallback may simplify presentation
- fallback must preserve semantic status and route identity
- renderers must expose required status, evidence, limitations, and action
  posture
- renderers must not invent facts or decide policy

## Boundaries

TSIS-00 is not a runtime implementation, launch, or deployment task. It does not
write `site/dist`, mutate public/master indexes, fetch files, OCR, extract, call
models, call sources, or enable public live fanout. Runtime Surface Kernel
implementation is deferred to a later TSIS phase.
