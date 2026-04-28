# GitHub Pages Deployment

GitHub Pages Deployment Enablement v0 configures a static only deployment path
for Eureka's current public artifact:

```text
public_site/
```

It does not host the Python backend, does not enable live probes, make live
Internet Archive calls, configure a custom domain, add deployment secrets,
deploy generated `site/dist/`, or make Eureka production-ready. This is not
production approval.

Eureka is not production.

## Workflow

Workflow path:

```text
.github/workflows/pages.yml
```

The workflow runs on pushes to `main` and can also be started with
`workflow_dispatch`.

Required workflow permissions:

```yaml
contents: read
pages: write
id-token: write
```

The workflow validates before upload:

```bash
python scripts/generate_public_data_summaries.py --check
python scripts/validate_publication_inventory.py
python scripts/validate_public_static_site.py
python scripts/check_github_pages_static_artifact.py
python scripts/validate_static_host_readiness.py
python scripts/validate_live_backend_handoff.py
```

Then it configures Pages, uploads `public_site/` with
`actions/upload-pages-artifact`, and deploys with `actions/deploy-pages`.

No Node, npm, frontend framework, generated site build, backend process, or
runtime server step is part of this workflow. Static Site Generation Migration
v0 builds `site/dist/` for validation, but this workflow still uploads
`public_site/`.

## Repository Settings

The workflow may exist before GitHub Pages is enabled in repository settings.
If the first run does not publish, a repository owner may need to enable Pages
for GitHub Actions in the GitHub repository UI:

```text
Settings -> Pages -> Build and deployment -> Source: GitHub Actions
```

This repository does not add custom domain configuration in this milestone.
No `CNAME` file is added.

Custom Domain / Alternate Host Readiness v0 adds readiness inventories,
operator docs, base-path policy, and `scripts/validate_static_host_readiness.py`
for future custom-domain or alternate-static-host work. It still does not
configure a custom domain, add DNS, add `public_site/CNAME`, or deploy an
alternate host.

Live Backend Handoff Contract v0 reserves future `/api/v1` backend route
families and disabled capability flags. GitHub Pages still serves only static
files; it does not make `/api/v1` live, proxy to Python, or provide a
production API.

No deployment secrets are required.

## URL And Base Path

The publication inventory defines the GitHub Pages project-site target:

```text
https://julesc013.github.io/eureka/
```

Project Pages uses the base path:

```text
/eureka/
```

The static artifact should therefore use relative internal links and avoid
root-relative links such as `/sources.html`.

## Artifact Safety

The Pages artifact is `public_site/` only.

Generated Public Data Summaries v0 commits static JSON under
`public_site/data/`; those files are part of the static artifact and are checked
for freshness and static-only safety before upload. They are not live API
routes and do not include live probes or external observations.

Lite/Text/Files Seed Surfaces v0 commits static compatibility outputs under
`public_site/lite/`, `public_site/text/`, and `public_site/files/`; those files
are part of the static artifact and are generated from public data summaries.
They are not live search, executable downloads, signed snapshots, relay
runtime, or native-client runtime behavior.

Static Resolver Demo Snapshots v0 commits static fixture-backed examples under
`public_site/demo/`; those files are part of the static artifact and are
generated from governed public data plus Python-oracle fixture outputs. They
are not live search, a live API, backend hosting, external observations, or
production resolver behavior.

Generated `site/dist/` output is not uploaded by this workflow yet. A later
artifact migration must explicitly prove equivalence and update this document,
the publication inventory, and the workflow together.

The artifact checker rejects Python/runtime source files, local stores, SQLite
databases, `.env` files, cache directories, backend directories, root-relative
internal links, and private local path patterns inside the artifact.

The deployment target remains static-only:

- no Python backend
- no live source probes
- no live Internet Archive access
- no auth or accounts
- no repository secrets
- no custom domain
- no production-ready claim

## Rollback

If a bad static deployment is published:

1. Revert the bad commit and push the revert to `main`.
2. Re-run the GitHub Pages workflow from Actions if needed.
3. Disable the workflow if repeated publishing must stop.
4. Disable Pages in repository settings if the public site must be taken down.

Do not treat rollback as a backend rollback. This workflow publishes only static
files.

## Known Limitations

- No server-side Python runs on GitHub Pages.
- No backend status exists beyond static pages and static data.
- No auth, accounts, rate limiting, process manager, or custom TLS ownership is
  supplied by this repo.
- No live source calls, crawling, scraping, or automated external searches are
  enabled.
- A workflow file or queued run is not proof that a public deployment
  succeeded. Deployment success requires GitHub Actions evidence.
