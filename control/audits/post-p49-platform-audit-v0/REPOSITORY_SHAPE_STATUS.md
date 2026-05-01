# Repository Shape Status

| Check | Evidence | Classification | Notes |
|---|---|---|---|
| Active static artifact | `site/dist` exists with `.eureka-static-site-generated` | `implemented_static_artifact` | Build and validation commands passed. |
| `public_site/` active root | `Test-Path public_site` returned false | `implemented_static_artifact` | Remaining `public_site` references are historical audit/planning evidence. |
| `third_party/` active root | `Test-Path third_party` returned false | `implemented_static_artifact` | `external/` is present as the outside-reference root. |
| Generated artifact ownership | `control/inventory/generated_artifacts/` and drift guard | `implemented_runtime` | `check_generated_artifact_drift.py` passed. |
| Layout validator | `scripts/validate_repository_layout.py` | `implemented_runtime` | Reports `static_artifact_root: site/dist`. |
| GitHub Pages workflow path | `.github/workflows/pages.yml` | `implemented_static_artifact` | Workflow uploads `site/dist`. |

Stale reference finding: `rg public_site|third_party` still finds historical
references in older audit packs and older planning artifacts. P50 records this
as an audit fact, not an active-root regression.
