# Eureka Repo Identity

- Project name: Eureka
- Canonical short namespace: `eureka`
- Repo state: bootstrap and pre-product

## Core Doctrine

- Plan first for any non-trivial task. Inspect the relevant paths, write a bounded plan, and update it as the work changes.
- Respect boundaries. Edit only the paths needed for the task and preserve the contract split between control, contracts, runtime, and surfaces.
- Verify before claiming completion. Run the lightweight checks that fit the scope and report what was actually verified.
- State blocked and deferred items explicitly. Do not imply completion by silence when something was left open on purpose.
- Treat placeholders honestly. Do not fabricate mature behavior, stable semantics, or fake completeness.

## High-Level Component Boundaries

- `control/` holds governance and planning material, not product runtime behavior.
- `contracts/` holds governed schemas, protocols, public API contracts, and shared UI contracts.
- `runtime/engine` owns engine behavior and service interfaces.
- `runtime/gateway` owns gateway-facing runtime behavior and depends on contracts plus engine-facing service interfaces.
- `runtime/connectors` implements bounded ingest, extract, and normalize adapters only.
- `surfaces/web` and `surfaces/native` are user-facing surfaces.
- `.aide/` owns repo operating metadata only.

## Dependency Law

- Web uses gateway public APIs and contracts in the normal path.
- Native uses contracts and gateway public APIs in the normal path.
- Native may use `runtime/engine/sdk` only if an explicit offline or local mode is deliberately adopted later.
- Engine must not depend on `surfaces/*`.
- Web must not depend on engine internals in the normal path.
- Connectors must not invent object truth.
- Connectors must not own trust semantics.
- AIDE does not own product semantics and must not define runtime behavior.

## Working Rules for Agents

- Keep changes narrowly scoped to the requested boundary.
- Prefer governed contract edits over hidden coupling.
- When a task crosses component boundaries, name the boundary crossing in the plan and in the final report.
- If verification cannot be completed, say so plainly and list the reason.
- If follow-up work is intentionally deferred, list it under a clear deferred or open-items heading.

