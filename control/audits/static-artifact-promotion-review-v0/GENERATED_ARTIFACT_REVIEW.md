# Generated Artifact Review

Generated artifact group: `static_site_dist`

Artifact paths:

- `site/dist`
- `site/dist/.eureka-static-site-generated`
- `site/dist/.nojekyll`

Generator commands:

- `python site/build.py`
- `python scripts/generate_public_data_summaries.py --check`
- `python scripts/generate_compatibility_surfaces.py --check`
- `python scripts/generate_static_resolver_demos.py --check`

Check commands:

- `python site/build.py --check`
- `python site/validate.py`
- `python scripts/check_github_pages_static_artifact.py --path site/dist`

Drift guard status: passed with
`python scripts/check_generated_artifact_drift.py --artifact static_site_dist`.

Manual edits allowed: false

Source inputs:

- `site/pages`
- `site/templates`
- `site/assets`
- `control/inventory/publication`
- `control/inventory/sources`
- `evals`
- `snapshots/examples/static_snapshot_v0`
- generator scripts for public data, compatibility surfaces, and demo snapshots

Known volatile fields: none for `static_site_dist`. Volatile fields remain
owned by narrower generated artifact groups where applicable, such as public
data build manifests.
