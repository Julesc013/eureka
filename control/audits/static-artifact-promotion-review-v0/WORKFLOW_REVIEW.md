# Workflow Review

Workflow path: `.github/workflows/pages.yml`

Workflow name: `Deploy static public site to GitHub Pages`

Triggers:

- push to `main`
- `workflow_dispatch`

Artifact upload path: `site/dist`

Validation steps before upload:

1. `python site/build.py`
2. `python scripts/generate_public_data_summaries.py --check`
3. `python scripts/generate_compatibility_surfaces.py --check`
4. `python scripts/generate_static_resolver_demos.py --check`
5. `python scripts/validate_publication_inventory.py`
6. `python site/validate.py`
7. `python scripts/check_github_pages_static_artifact.py --path site/dist`
8. `python scripts/check_generated_artifact_drift.py --artifact static_site_dist`

Review result:

- active workflow contains `public_site`: no
- workflow uploads `site/dist`: yes
- workflow configures Pages: yes
- workflow deploys with `actions/deploy-pages`: yes
- deployment success: unverified

Remaining manual review work: GitHub Pages Run Evidence Review v0 should inspect
the actual GitHub Actions run, artifact upload, Pages deployment result, and
served output before any deployment-success claim is made.
