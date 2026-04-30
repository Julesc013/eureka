# Validator Summary

Typed AI Output Validator v0 consists of:

- `runtime/engine/ai/typed_output_validator.py`
- `scripts/validate_ai_output.py`
- `control/inventory/ai_providers/typed_output_examples.json`
- focused runtime, script, and operations tests

The module validates provider manifests, future AI task requests, typed AI
output objects, typed AI output files, and explicit provider bundles. The CLI
validates all registered examples by default, one output file with `--output`,
or a provider bundle with `--bundle-root`.

All reports state that model calls, network calls, mutation, and import were
not performed.
