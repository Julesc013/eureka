# Public Alpha Hosting Pack v0

Public Alpha Hosting Pack v0 is a bounded operator evidence packet for a
supervised Eureka public-alpha demo rehearsal.

It bundles the current route inventory status, smoke-check expectations,
operator checklist links, known blockers, mode guidance, route safety summary,
and rehearsal runbook. It does not deploy Eureka and does not add deployment
infrastructure.

LIVE_ALPHA_00 Static Public Site Pack complements this operator packet with a
committed no-JS `public_site/` source tree for later static-hosting review. The
static pack is documentation only; it does not start a server, deploy Eureka,
add backend hosting, add live probes, scrape external systems, or approve open
public internet exposure.

LIVE_ALPHA_01 Production Public-Alpha Wrapper adds
`scripts/run_public_alpha_server.py` as a provider-neutral stdlib entrypoint for
future supervised public-alpha rehearsals. The wrapper performs no deployment,
adds no hosting provider configuration, keeps live probes and live Internet
Archive access disabled, defaults to localhost, and refuses nonlocal binds
without explicit operator acknowledgement.

Public Publication Plane Contracts v0 adds the public route, data, client
profile, deployment target, redirect, and base-path inventory layer that must
be validated before GitHub Pages or any later static-hosting enablement. That
contract slice did not deploy Eureka, add provider configuration, add a static
generator, or enable live backend behavior.

GitHub Pages Deployment Enablement v0 adds a static-only workflow and artifact
checker for uploading `public_site/` after validation. That workflow is not a
backend hosting path: it does not run Python, enable live probes, configure a
custom domain, add secrets, create a generator, or prove deployment success
without GitHub Actions evidence.

Static Site Generation Migration v0 later adds a stdlib-only `site/` generator
and `site/dist/` validation output. It does not change this hosting pack or the
Pages artifact: `public_site/` remains the deployable static artifact.

Generated Public Data Summaries v0 adds deterministic static JSON under
`public_site/data/` and `site/dist/data/`. Those summaries support later static
compatibility surfaces; they are not a live API, do not run backend code, do
not enable live probes, and do not record external observations.

## What This Pack Is

- an operator-readable packet for rehearsing the constrained `public_alpha`
  posture
- a guide to the existing route inventory and smoke evidence
- a runbook for checking safe routes, blocked routes, and status output
- a place to record rehearsal evidence and operator signoff
- a clear list of blockers before any real public hosting decision

## What This Pack Is Not

- not production-ready approval
- not open-internet approved
- intended for supervised demo rehearsal only
- not auth, accounts, HTTPS/TLS, rate limiting, logging, monitoring, process
  supervision, deployment configuration, Docker, nginx, systemd, or cloud
  infrastructure
- not a replacement for the route inventory, smoke script, or readiness review

## Intended Audience

This pack is for a trusted operator preparing a short-lived, supervised demo
rehearsal of the current stdlib web/API backend in `public_alpha` mode. It is
not meant for unsupervised hosting or open public internet exposure.

## Current Readiness Level

Current status: ready for local or tightly supervised public-alpha rehearsal
only when the runbook checks pass.

The current posture has evidence that safe read-only/search/inspect/eval routes
work and that caller-provided local path controls are blocked in
`public_alpha` mode. It is still blocked for open-internet production exposure.

## Related Artifacts

- Public Alpha Safe Mode v0:
  `docs/operations/PUBLIC_ALPHA_SAFE_MODE.md`
- Public Alpha Deployment Readiness Review:
  `docs/operations/PUBLIC_ALPHA_READINESS_REVIEW.md`
- Operator checklist:
  `docs/operations/PUBLIC_ALPHA_OPERATOR_CHECKLIST.md`
- Route inventory:
  `control/inventory/public_alpha_routes.json`
- Smoke script:
  `scripts/public_alpha_smoke.py`
- Static public site pack:
  `public_site/`
- Static site validator:
  `scripts/validate_public_static_site.py`
- Public Alpha Rehearsal Evidence v0:
  `docs/operations/public_alpha_rehearsal_evidence_v0/`
- Public Alpha Wrapper:
  `docs/operations/PUBLIC_ALPHA_WRAPPER.md`
- Wrapper config check:
  `python scripts/run_public_alpha_server.py --check-config`
- Publication inventory:
  `control/inventory/publication/`
- Publication inventory validator:
  `python scripts/validate_publication_inventory.py`
- GitHub Pages static deployment docs:
  `docs/operations/GITHUB_PAGES_DEPLOYMENT.md`
- GitHub Pages artifact checker:
  `python scripts/check_github_pages_static_artifact.py`

## Pack Contents

- `RUNBOOK.md`: step-by-step rehearsal process
- `ROUTE_SAFETY_SUMMARY.md`: human-readable route category summary
- `SMOKE_EVIDENCE_TEMPLATE.md`: blank evidence capture form
- `OPERATOR_SIGNOFF_TEMPLATE.md`: blank operator signoff checklist
- `BLOCKERS.md`: blockers before real public hosting
- `hosting_pack_manifest.json`: small machine-readable pack manifest

Use this pack as evidence for a rehearsal decision only. Do not treat it as a
production deployment packet.
