# Validation Report

Focused validation commands:

```text
python -m unittest tests.runtime.test_ia_metadata_provider_fallback
python -m unittest tests.runtime.test_surface_ia_metadata_fallback
python -m unittest tests.evals.test_ia_metadata_fallback_smoke
```

Result: `PASS`

Additional validation:

```text
python -m json.tool evals\hard_queries\metadata_fallback_smoke\ia_00\query_inputs.json
python -m json.tool evals\hard_queries\metadata_fallback_smoke\ia_00\ia_metadata_fixtures.json
python -m json.tool evals\hard_queries\metadata_fallback_smoke\ia_00\expected_fallback_outputs.json
python -m json.tool evals\hard_queries\metadata_fallback_smoke\ia_00\surface_projection_fixtures.json
python -m json.tool evals\hard_queries\metadata_fallback_smoke\ia_00\renderer_expected_outputs.json
```

Result: `PASS`
