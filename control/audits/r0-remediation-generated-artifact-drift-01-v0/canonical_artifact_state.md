# Canonical Artifact State

Canonical generated artifacts were refreshed through repo-local generators and validators:

- public search index: `python scripts/build_public_search_index.py --check`
- static site: `python site/validate.py`
- compatibility surfaces: `python scripts/generate_compatibility_surfaces.py --check`
- GitHub Pages artifact: `python scripts/check_github_pages_static_artifact.py --path site/dist`
- demand dashboard examples: `python scripts/validate_demand_dashboard_contract.py --json`
- demand dashboard snapshots: `python scripts/validate_demand_dashboard_snapshot.py --all-examples --json`

No hosted deployment or master index mutation was performed.
