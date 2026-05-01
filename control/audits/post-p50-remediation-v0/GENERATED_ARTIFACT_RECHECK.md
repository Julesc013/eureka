# Generated Artifact Recheck

P51 rechecks the static/generated artifact lane with:

```text
python site/build.py --check
python site/validate.py
python scripts/validate_publication_inventory.py
python scripts/validate_public_static_site.py
python scripts/check_github_pages_static_artifact.py --path site/dist
python scripts/check_generated_artifact_drift.py
```

Result summary is recorded in `COMMAND_RESULTS.md` and
`post_p50_remediation_report.json`.

No generated artifact is intentionally used to hide unrelated behavior changes.
