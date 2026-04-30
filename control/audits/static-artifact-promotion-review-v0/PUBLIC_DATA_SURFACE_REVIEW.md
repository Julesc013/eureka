# Public Data Surface Review

Reviewed surfaces:

| Path | Status | Notes |
| --- | --- | --- |
| `site/dist/data/` | present and valid | 6 generated JSON summaries |
| `site/dist/lite/` | present and valid | no-JS compatibility HTML |
| `site/dist/text/` | present and valid | plain text compatibility output |
| `site/dist/files/` | present and valid | file-tree manifest and checksums |
| `site/dist/demo/` | present and valid | fixture-backed resolver examples |
| `site/dist/assets/` | present | static CSS only |
| `site/dist/.nojekyll` | present | required for verbatim Pages serving |

Validation commands:

- `python scripts/generate_public_data_summaries.py --check`
- `python scripts/generate_compatibility_surfaces.py --check`
- `python scripts/generate_static_resolver_demos.py --check`
- `python scripts/validate_public_static_site.py --site-root site/dist`
- `python site/validate.py`

Snapshot references remain repo-local examples under
`snapshots/examples/static_snapshot_v0/`. They are not executable downloads,
production snapshots, signed releases, or consumer runtime behavior.
