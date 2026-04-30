# Workflow Configuration

Workflow path: `.github/workflows/pages.yml`

Workflow name: `Deploy static public site to GitHub Pages`

Triggers:

- `push` to `main`
- `workflow_dispatch`

Permissions:

- `contents: read`
- `pages: write`
- `id-token: write`

Job:

- `deploy`
- Display name: `Validate and deploy site/dist`
- Runner: `ubuntu-latest`
- Environment: `github-pages`
- Environment URL expression: `${{ steps.deployment.outputs.page_url }}`

Validation steps before upload:

1. `python site/build.py`
2. `python scripts/generate_public_data_summaries.py --check`
3. `python scripts/generate_compatibility_surfaces.py --check`
4. `python scripts/generate_static_resolver_demos.py --check`
5. `python scripts/validate_publication_inventory.py`
6. `python site/validate.py`
7. `python scripts/check_github_pages_static_artifact.py --path site/dist`
8. `python scripts/check_generated_artifact_drift.py --artifact static_site_dist`

Pages actions:

- Configure action: `actions/configure-pages@v5`
- Upload action: `actions/upload-pages-artifact@v3`
- Upload path: `site/dist`
- Deploy action: `actions/deploy-pages@v4`

Review:

- Uploads `site/dist`: yes.
- Active workflow contains `public_site`: no.
- Static-only: yes.
- Backend hosting behavior: no.
- Live source probes or search scraping: no.
- Node/npm build chain: no.
