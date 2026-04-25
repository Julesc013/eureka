# Public Alpha

Public hosting is not the next step. It is a later milestone that should begin
only after the backend has a safer and more coherent operational shape.

## Minimum Requirements Before Hosting

The minimum public-alpha entry gate should include:

- Source Registry v0 (implemented)
- Resolution Run Model v0 (implemented)
- Query Planner v0 (implemented)
- Local Index v0 (implemented)
- Local Worker and Task Model v0 (implemented)
- Resolution Memory v0 (implemented, local-only)
- Archive Resolution Eval Runner v0 (implemented as a local regression guardrail)
- Public Alpha Safe Mode v0 (implemented as constrained mode-aware server behavior)
- Public Alpha Deployment Readiness Review (implemented as route inventory,
  smoke checks, and operator checklist)
- local-path APIs disabled or explicitly restricted in public-alpha mode
- safe status route without private local path disclosure
- repeatable public-alpha smoke report
- clear alpha disclaimers

## Public Alpha Safe-Mode Expectations

A public alpha should assume:

- no unrestricted filesystem path access
- no private user memory
- no hidden access to local store roots outside configured safe paths
- no hidden access to local memory-store roots outside configured safe paths
- no assumption that auth or user accounts exist yet
- no silent escalation from local bootstrap behavior into public network
  behavior

## What The Alpha Should Include

A credible small public alpha should be able to expose:

- search
- exact resolution
- evidence visibility
- miss explanation
- representation and access-path visibility
- bounded next-step guidance
- safe fixture readback only after a later explicit route review

## What The Alpha Should Not Include

The public alpha should not yet include:

- installer automation
- account system
- private user memory
- large-scale crawling
- background OCR
- broad downloads
- native app sync

## Current Status

Public Alpha Safe Mode v0 is now implemented as mode-aware stdlib web/API
server behavior. `local_dev` preserves trusted local path demos, while
`public_alpha` blocks arbitrary local path parameters and disables local
write/readback route groups. Public Alpha Deployment Readiness Review now adds
`control/inventory/public_alpha_routes.json`, `scripts/public_alpha_smoke.py`,
and operator docs under `docs/operations/`. Public hosting itself is still not
started. The hosted-alpha gate remains blocked on real deployment posture,
externally supplied auth/TLS decisions, abuse controls, operational monitoring,
and final operator approval.
