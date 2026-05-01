# Generated Artifact Review

P56 updates generated static artifacts through the existing site generator and
compatibility-surface generator.

Generated outputs:

- `site/dist/search.html`
- `site/dist/lite/search.html`
- `site/dist/text/search.txt`
- `site/dist/files/search.README.txt`
- `site/dist/data/search_config.json`
- `site/dist/data/public_index_summary.json`

The generated artifact registry includes `static_search_integration` so drift
can be checked with:

```powershell
python scripts/check_generated_artifact_drift.py --artifact static_search_integration
```

Manual edits to generated outputs are not allowed. Source inputs and generator
code must be updated instead.
