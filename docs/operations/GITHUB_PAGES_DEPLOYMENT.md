# GitHub Pages Deployment

GitHub Pages Deployment Enablement v0 configures a static only deployment path
for Eureka's current public artifact:

```text
site/dist/
```

It does not host the Python backend, does not enable live probes, make live
Internet Archive calls, configure a custom domain, add deployment secrets,
prove that generated `site/dist/` has been deployed, or make Eureka
production-ready. This is not production approval.

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
python site/build.py
python scripts/generate_public_data_summaries.py --check
python scripts/generate_compatibility_surfaces.py --check
python scripts/generate_static_resolver_demos.py --check
python scripts/validate_publication_inventory.py
python site/validate.py
python scripts/check_github_pages_static_artifact.py --path site/dist
python scripts/check_generated_artifact_drift.py --artifact static_site_dist
```

Then it configures Pages, uploads `site/dist/` with
`actions/upload-pages-artifact`, and deploys with `actions/deploy-pages`.

No Node, npm, frontend framework, backend process, or runtime server step is
part of this workflow. Repository Shape Consolidation v0 makes `site/dist/`
the single generated static artifact for this workflow.
Static Artifact Promotion Review v0 conditionally promotes `site/dist/` as the
active repo-local static publication artifact, but GitHub Actions deployment
success depends on run evidence.
GitHub Pages Run Evidence Review v0 records that the current-head workflow run
failed at `actions/configure-pages@v5` because the repository Pages site was
not found/enabled for GitHub Actions. The static build and validation steps
passed before that failure, but artifact upload and deployment were skipped.
Static Deployment Evidence / GitHub Pages Repair v0 records that the workflow
still targets `site/dist` and local artifact validation passes, but `gh` is not
available in this environment. Current-head Actions and Pages API state are
therefore unverified by P52, while the committed prior run evidence remains a
failed Pages configuration run.

## Repository Settings

The workflow may exist before GitHub Pages is enabled in repository settings.
If the first run does not publish, a repository owner may need to enable Pages
for GitHub Actions in the GitHub repository UI:

```text
Settings -> Pages -> Build and deployment -> Source: GitHub Actions
```

P51 local remediation does not change repository settings. The remaining
operator steps are:

1. Open the GitHub repository settings.
2. Go to `Settings -> Pages`.
3. Set `Build and deployment -> Source` to `GitHub Actions`.
4. Re-run the Pages workflow for the commit being verified.
5. Confirm that `Configure GitHub Pages`, artifact upload, and deploy steps all
   complete.
6. Record the workflow run URL, deployment URL, deployed commit SHA, and
   timestamp in a future run-evidence audit.
7. Open the deployed root page, status page, sources page, search handoff page,
   lite surface, text surface, and files surface.
8. Record screenshot or text evidence if desired, then update a future evidence
   audit with the run URL and deployed commit.

Until that evidence exists, the local state is `workflow_configured` and
`deployment_unverified`; Pages enablement remains operator-gated.

This repository does not add custom domain configuration in this milestone.
No `CNAME` file is added.

Custom Domain / Alternate Host Readiness v0 adds readiness inventories,
operator docs, base-path policy, and `scripts/validate_static_host_readiness.py`
for future custom-domain or alternate-static-host work. It still does not
configure a custom domain, add DNS, add `site/dist/CNAME`, or deploy an
alternate host.

Live Backend Handoff Contract v0 reserves future `/api/v1` backend route
families and disabled capability flags. GitHub Pages still serves only static
files; it does not make `/api/v1` live, proxy to Python, or provide a
production API.

Public Search Static Handoff v0 adds `search.html`, `lite/search.html`,
`text/search.txt`, `files/search.README.txt`, and
`data/search_handoff.json` to `site/dist`. These are static handoff artifacts:
the hosted backend URL is not configured or verified, the form is disabled for
hosted search, and GitHub Pages still does not run Python.

Live Probe Gateway Contract v0 records disabled future source-probe policy.
GitHub Pages still performs no source probes, URL fetches, Internet Archive
calls, scraping, crawling, or downloads.

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

The Pages artifact is `site/dist/` only.

Generated Public Data Summaries v0 commits static JSON under
`site/dist/data/`; those files are part of the static artifact and are checked
for freshness and static-only safety before upload. They are not live API
routes and do not include live probes or external observations.

Lite/Text/Files Seed Surfaces v0 commits static compatibility outputs under
`site/dist/lite/`, `site/dist/text/`, and `site/dist/files/`; those files
are part of the static artifact and are generated from public data summaries.
They are not live search, executable downloads, signed snapshots, relay
runtime, or native-client runtime behavior.

Static Resolver Demo Snapshots v0 commits static fixture-backed examples under
`site/dist/demo/`; those files are part of the static artifact and are
generated from governed public data plus Python-oracle fixture outputs. They
are not live search, a live API, backend hosting, external observations, or
production resolver behavior.

Repository Shape Consolidation v0 promotes generated `site/dist/` output as
the single Pages artifact uploaded by this workflow.
Static Artifact Promotion Review v0 confirms local artifact readiness.
GitHub Pages Run Evidence Review v0 records the current Actions evidence as a
failed Pages configuration run: local artifact checks passed, no Pages artifact
was uploaded, no deployment URL was emitted, and deployment success is not
claimable.

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
- Current evidence shows the workflow fails before artifact upload until the
  repository Pages site is enabled/configured for GitHub Actions or the
  workflow is repaired under an approved follow-up.

## P77 Pages Evidence

P77 checked `https://julesc013.github.io/eureka/` from repo config and received 404 responses for root, `search.html`, `data/search_config.json`, and `data/public_index_summary.json`. Pages/static hosting needs operator repair or verification before a static-live claim.
