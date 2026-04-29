# Public Alpha

Public backend hosting is not the next step. Static GitHub Pages enablement now
exists for `public_site/`, but hosted backend exposure remains a later
milestone that should begin only after the backend has a safer and more
coherent operational shape.

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
- Public Alpha Rehearsal Evidence v0 (implemented as local/static
  evidence/runbook material, not deployment approval)
- LIVE_ALPHA_01 Production Public-Alpha Wrapper (implemented as a stdlib
  entrypoint/config guard for supervised public-alpha runs; no deployment and
  no live probes)
- Public Publication Plane Contracts v0 (implemented as route, data, client,
  deployment-target, redirect, base-path, and claim-traceability governance;
  no deployment, generator, or live backend behavior)
- GitHub Pages Deployment Enablement v0 (implemented as static-only workflow
  configuration for `public_site/`; no backend deployment, live probes, custom
  domain, generator, or verified deployment-success claim)
- Static Site Generation Migration v0 (implemented as a stdlib-only `site/`
  source/generator tree producing `site/dist/` for validation; `public_site/`
  remains the deployment artifact)
- Generated Public Data Summaries v0 (implemented as deterministic static JSON
  under `public_site/data/` and `site/dist/data/`; no live API, live probes,
  external observations, or production JSON stability claim)
- Lite/Text/Files Seed Surfaces v0 (implemented as static no-JS/no-download
  compatibility seed surfaces under `public_site/lite/`, `public_site/text/`,
  and `public_site/files/`; no live search, snapshots, relay/native runtime,
  executable downloads, or production support claim)
- Static Resolver Demo Snapshots v0 (implemented as static no-JS
  fixture-backed resolver examples under `public_site/demo/`; no live search,
  live API, backend hosting, external observations, or production behavior)
- Custom Domain / Alternate Host Readiness v0 (implemented as static-host
  portability inventories, docs, checklist, and validation; no DNS, CNAME,
  alternate-host deployment, provider config, backend hosting, or live probes)
- Live Backend Handoff Contract v0 (implemented as contract-only `/api/v1`
  route reservations, capability flags, and error-envelope expectations; no
  live backend, live probes, backend hosting, or production API guarantee)
- Live Probe Gateway Contract v0 (implemented as disabled-by-default source
  probe policy, candidate-source caps, cache/evidence expectations, and
  operator gates; no live probes, network calls, downloads, scraping, or
  Internet Archive access)
- Compatibility Surface Strategy v0 (implemented as strategy, capability
  matrix, route matrix, old-client degradation policy, and
  native/snapshot/relay readiness guidance; no new runtime behavior,
  snapshots, relay services, native apps, live API behavior, or live probes)
- Signed Snapshot Format v0 (implemented as a static/offline snapshot contract
  and repo seed example under `snapshots/examples/static_snapshot_v0/`; no real
  signing keys, production signatures, executable downloads, public
  `/snapshots/` route, relay runtime, native-client runtime, or live behavior)
- Signed Snapshot Consumer Contract v0 (implemented as contract/design only for
  future file-tree, text, lite HTML, relay, native, and audit snapshot
  consumers; no snapshot reader runtime, relay runtime, native client,
  production signing, real keys, executable downloads, live backend, or live
  probes)
- Native Client Contract v0 (implemented as contract/design only for future
  Windows/macOS/native client lanes and readiness gates; no Visual Studio/Xcode
  projects, native GUI, FFI, installers, downloads, relay sidecars, live
  probes, Rust runtime wiring, or production native-client claim)
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
Public Alpha Rehearsal Evidence v0 now adds
`docs/operations/public_alpha_rehearsal_evidence_v0/` plus a local generator
and check script. It records static-site validation, public-alpha smoke,
route-inventory, eval/audit, external-baseline pending status, blocker, and
unsigned signoff evidence. It performs no deployment, approves no production
hosting, adds no live probes, and records no external observations.
LIVE_ALPHA_01 Production Public-Alpha Wrapper now adds
`scripts/run_public_alpha_server.py` plus a bounded public-alpha config model.
The wrapper defaults to localhost, refuses unsupported modes, guards nonlocal
binds, reports safe capability flags, disables local path controls, downloads,
user storage, live probes, and live Internet Archive access, and still performs
no deployment or production approval.
Public Publication Plane Contracts v0 now adds
`control/inventory/publication/`, `docs/architecture/PUBLICATION_PLANE.md`,
reference docs, a stdlib inventory validator, and tests. It commits the
distinction between the current `public_site/` artifact, future `site/`
generator source, and future `site/dist/` generated artifact before GitHub
Pages or custom-domain work. The contract slice itself performed no deployment,
added no GitHub Pages workflow, created no generator, enabled no live backend,
and recorded no external observations.

GitHub Pages Deployment Enablement v0 now adds the static-only Pages workflow,
artifact checker, operations docs, and tests for publishing only `public_site/`
after validation. This does not change public-alpha backend readiness: it does
not host the Python backend, enable live probes, configure a custom domain, add
a generator, add secrets, or claim deployment success without GitHub Actions
evidence.

Static Site Generation Migration v0 now adds `site/`, `site/build.py`,
`site/validate.py`, page JSON, templates, and generated `site/dist/` output.
The generated output is validation evidence, not the GitHub Pages artifact yet.
This keeps public-alpha backend readiness unchanged and adds no Node/npm,
frontend framework, live backend behavior, live probes, custom domain, or
production-readiness claim.

Generated Public Data Summaries v0 now adds static JSON summaries under
`public_site/data/` and `site/dist/data/` for page, source, eval, route, and
build state. Lite/Text/Files Seed Surfaces v0 now consumes those summaries to
publish static compatibility seed surfaces under `public_site/lite/`,
`public_site/text/`, and `public_site/files/`. These files are not a live API,
do not host backend behavior, do not enable live probes, do not record external
observations, do not add executable downloads, and do not create production
signed snapshots, public `/snapshots/` routes, relay behavior, or native-client runtime.

Static Resolver Demo Snapshots v0 now publishes static fixture-backed examples
under `public_site/demo/` and generated validation copies under
`site/dist/demo/`. These examples show current bounded resolver behavior for
query planning, member-level results, compatibility evidence, absence,
comparison, source detail, article/scan fixtures, and eval summaries. They do
not add live search, a live API, external observations, backend hosting, or
production behavior.

Custom Domain / Alternate Host Readiness v0 now records future custom-domain
and alternate-static-host prerequisites, base-path portability, and an operator
checklist. It adds no DNS records, no `CNAME`, no provider config, no alternate
host deployment, no backend hosting, no live probes, and no production claim.

Live Backend Handoff Contract v0 now records future `/api/v1` endpoint
reservations, disabled live capability flags, static-to-live handoff policy, and
error-envelope expectations. It is a contract-only public-alpha input: it does
not host a backend, make `/api/v1` live, enable live probes, configure CORS/auth
or rate limits for production, or make a stable public API guarantee.

Live Probe Gateway Contract v0 now records the future source-probe gateway
policy that any hosted backend would have to obey before external metadata
probes exist. It keeps all candidates future-disabled, keeps public-alpha live
probes disabled by default, keeps Google manual-baseline-only, and adds no
Internet Archive calls, URL fetching, scraping, crawling, downloads, adapters,
or production source behavior.

Relay Surface Design v0 now records the future local/LAN relay posture for old
or constrained clients. It is public-alpha-adjacent contract work only: no relay
runtime, network listener, FTP, SMB, WebDAV, protocol proxy, private data
exposure, write/admin route, live-probe passthrough, backend hosting, or
production relay claim is added.

## Public Alpha Checkpoint

Post-Queue State Checkpoint v0 records the current post-queue evidence and
verification state under `control/audits/post-queue-state-checkpoint-v0/`. It
is audit/reporting only; it does not add backend hosting, live probes,
production deployment, Rust runtime wiring, relay services, or native app
projects.
