# Static Publication Status

| Area | Evidence | Classification | Notes |
|---|---|---|---|
| Static generator | `python site/build.py --check` | `implemented_runtime` | Passed. |
| Generated static artifact | `site/dist` | `implemented_static_artifact` | `site/build.py --json` passed. |
| Static validator | `python site/validate.py` and `--json` | `implemented_runtime` | 9 pages validated. |
| Public data summaries | `site/dist/data/*.json` | `implemented_static_artifact` | 7 generated data files checked. |
| Lite/text/files surfaces | `site/dist/lite`, `site/dist/text`, `site/dist/files` | `implemented_static_artifact` | 21 compatibility files checked. |
| Static resolver demos | `site/dist/demo` | `fixture_only` | 8 fixture-backed demos checked. |
| GitHub Pages workflow | `.github/workflows/pages.yml` | `implemented_static_artifact` | Upload path is `site/dist`. |
| Pages deployment evidence | `github_pages_run_evidence_report.json` | `blocked` | Recorded current-head run failed at `actions/configure-pages@v5`; no artifact upload or deployment URL. |

The static host does not claim a dynamic backend. GitHub Pages remains a
static-only target.
