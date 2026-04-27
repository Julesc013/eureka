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
- Public Alpha Hosting Pack v0 (implemented as a supervised rehearsal evidence
  packet)
- LIVE_ALPHA_00 Static Public Site Pack (implemented as a no-JS static site
  source pack for later hosting review, not deployment)
- Search Usefulness Audit v0 (implemented as a local usefulness/backlog audit
  with no external scraping)
- Comprehensive Test/Eval Operating Layer and Repo Audit v0 (implemented as
  structured verification lanes and audit findings; not a hosting approval)
- Hard Test Pack v0 (implemented as regression guards for path leakage, route
  inventory drift, external baseline honesty, and docs/command drift; not a
  hosting approval)
- local-path APIs disabled or explicitly restricted in public-alpha mode
- safe status route without private local path disclosure
- source capability and coverage-depth projection limited to governed metadata
  with no private local path disclosure
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
and operator docs under `docs/operations/`. Public Alpha Hosting Pack v0 now
adds `docs/operations/public_alpha_hosting_pack/` plus a route-summary
generator for supervised rehearsal evidence. Public hosting itself is still not
started. The hosted-alpha gate remains blocked on real deployment posture,
externally supplied auth/TLS decisions, abuse controls, operational monitoring,
and final operator approval. Search Usefulness Audit v0 now provides a broad
local query/usefulness report that can inform public-alpha demo scope, but its
external Google and Internet Archive baselines remain pending manual
observation and it is not public-hosting approval.
Comprehensive Test/Eval Operating Layer and Repo Audit v0 adds reusable
public-alpha and full verification lanes plus hard-test proposals for path
leakage and route inventory drift, but it does not change the public-alpha
runtime posture or approve public hosting.
Hard Test Pack v0 now makes the first path-leakage and route-inventory drift
guards executable, while still avoiding deployment infrastructure, auth, TLS,
accounts, rate limiting, or production-readiness claims.
Source Coverage and Capability Model v0 adds safe source capability and
coverage-depth metadata to source pages and API responses in public-alpha mode.
This is descriptive registry projection only; it does not add live source
probing, source sync, crawling, or implemented placeholder connectors.
LIVE_ALPHA_00 Static Public Site Pack now adds `public_site/`, a plain static
HTML/CSS public-facing documentation pack with status, source matrix,
eval/audit state, demo queries, limitations, roadmap, and local quickstart
pages. The pack is static only: it starts no server, performs no deployment,
adds no backend hosting, makes no live source calls, performs no scraping, and
does not claim production readiness.
