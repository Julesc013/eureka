# Static Artifact Review

Artifact root:

```text
site/dist
```

Serial local validation results:

| Command | Status | Notes |
|---|---:|---|
| `python site/build.py --check` | pass | Temporary build validated. |
| `python site/build.py --json` | pass | Regenerated `site/dist` deterministically; no deployment. |
| `python site/validate.py` | pass | 9 pages; dist validation valid. |
| `python site/validate.py --json` | pass | 7 data files, 21 compatibility files, 11 demo files. |
| `python scripts/validate_publication_inventory.py` | pass | 49 registered routes. |
| `python scripts/validate_public_static_site.py` | pass | 9 pages and 15 source IDs checked. |
| `python scripts/check_github_pages_static_artifact.py --path site/dist` | pass | Artifact is valid for Pages upload. |
| `python scripts/check_generated_artifact_drift.py --artifact static_site_dist` | pass | `static_site_dist` group passed. |

An initial concurrent validation attempt observed transient missing files while
`site/build.py --json` was mutating `site/dist`. That was a command-ordering
issue in the audit run, not persistent artifact drift. The serial recheck
passed.
