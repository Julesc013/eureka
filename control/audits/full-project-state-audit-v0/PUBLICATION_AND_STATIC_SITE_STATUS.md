# Publication and Static Site Status

Publication plane:

- Governed publication inventories are present under `control/inventory/publication/`.
- `python scripts/validate_publication_inventory.py` passed.
- Registered routes: 43
- Current public static pages: 8
- Required client profiles: 9
- Required public data paths: 10

Static site:

- `public_site/` is the current static artifact.
- `site/` and `site/dist/` are generated-site source/output, but `public_site/` remains the current deployable artifact.
- `python scripts/validate_public_static_site.py` passed.
- `python site/build.py --check` passed.
- `python site/validate.py` passed.

Static surfaces:

- `public_site/data/`: 6 generated public data files.
- `public_site/lite/`, `public_site/text/`, `public_site/files/`: 18 compatibility surface files.
- `public_site/demo/`: 8 static resolver demos, 11 files.
- Snapshot seed: 12 files, 11 checksum entries.

GitHub Pages:

- Static workflow/config is present.
- `python scripts/check_github_pages_static_artifact.py` passed.
- Deployment status remains workflow-configured but deployment success unverified in this audit.

Primary risk: generated artifact drift between `site/`, `site/dist/`, `public_site/`, and publication inventories.
