# Validation

Focused J0 validation passed for:

- `python scripts/validate_safe_actions_runtime.py`
- `python scripts/build_action_manifest.py --action view --subject examples/actions/manifests/view_action_manifest_v0.json --check`
- `python scripts/build_acquisition_manifest.py --subject examples/actions/acquisition/acquisition_manifest_metadata_only_v0.json --check`
- `python scripts/build_citation_bundle.py --subject examples/actions/citation/citation_bundle_object_v0.json --check`
- `python scripts/build_export_manifest.py --subject examples/actions/export/export_manifest_object_v0.json --check`
- `python scripts/summarize_action_manifests.py --input examples/actions --check`
- `python -m unittest tests.actions.test_safe_action_manifests`
- `python -m unittest tests.actions.test_acquisition_manifest`
- `python -m unittest tests.actions.test_citation_export_preservation`
- `python -m unittest tests.operations.test_safe_action_scripts`
