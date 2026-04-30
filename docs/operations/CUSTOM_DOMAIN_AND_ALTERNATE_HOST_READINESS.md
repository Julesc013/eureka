# Custom Domain And Alternate Host Readiness

Custom Domain / Alternate Host Readiness v0 prepares Eureka's static
publication plane for future host portability. It does not configure a custom
domain, add DNS records, commit a `CNAME` file, deploy to alternate hosts, add
provider secrets, host the Python backend, enable live probes, or approve
production use.

Current state:

- GitHub Pages project publishing is configured for the static `site/dist/`
  artifact.
- The GitHub Pages project base path is `/eureka/`.
- Deployment success is unverified unless a GitHub Actions run proves it.
- No custom domain configured.
- No DNS changes are performed by this repo.
- No `site/dist/CNAME` file is committed.
- No alternate static host is configured.
- No backend hosting or live source probing is enabled.
- No live probes are configured.
- No live source probing is configured.
- `/api/v1` live backend handoff is not active.

Live Backend Handoff Contract v0 is separate from this static-host readiness
layer. A custom domain or alternate static host would still be static-only
unless a later backend deployment milestone explicitly configures live backend
handoff.

## Future Host Targets

Readiness detail lives in
`control/inventory/publication/static_hosting_targets.json`.

The current target is `github_pages_project`, which serves static files from
`site/dist/` under `/eureka/`.

Future candidates are:

- `github_pages_custom_domain`: static GitHub Pages at `/` after ownership
  verification and a later explicit domain task.
- `cloudflare_pages_static`: future static-only alternate host, with no
  functions or provider config committed by this repo slice.
- `generic_static_host`: any static host that can serve HTML, JSON, text, and
  checksum files without backend behavior.
- `local_file_preview`: local static-file inspection only; not public hosting.

## Base-Path Portability

Static pages must work under both:

```text
/eureka/
/
```

Internal page, data, demo, lite, text, and files-surface links should therefore
remain relative. Root-relative links such as `/status.html` are not acceptable
inside static artifacts because they break GitHub Pages project hosting.

Absolute canonical URLs must not be added until a future domain task updates
the publication inventory and validates the chosen host.

## Custom Domain Prerequisites

A later custom-domain task must complete at least:

- choose and record the intended domain
- verify domain ownership in the hosting provider outside this repo
- review DNS changes outside this repo
- decide whether a future `CNAME` file or Pages setting is appropriate
- run `python scripts/validate_static_host_readiness.py`
- run `python scripts/validate_publication_inventory.py`
- run `python scripts/validate_public_static_site.py`
- run `python scripts/check_github_pages_static_artifact.py`
- confirm no backend, live-probe, or production-ready claim was introduced
- record rollback/removal steps
- record operator signoff

## Takeover Risk

Custom-domain work can create takeover risk if DNS points to a host binding
that is missing, removed, or controlled by the wrong account. Eureka therefore
keeps DNS and domain binding outside this readiness slice and requires future
operator verification before any domain is made active.

## Prohibited Claims

Until a future task actually configures and verifies a host, public docs and
static artifacts must not claim:

- custom domain configured
- alternate host configured
- DNS records applied
- `CNAME` committed
- backend deployed
- live probes enabled
- production ready
- public deployment succeeded

## Rollback Considerations

Future host changes must document how to remove the host binding, revert static
artifact changes, remove or change DNS outside the repo, and return to the
GitHub Pages project-path target if needed.
