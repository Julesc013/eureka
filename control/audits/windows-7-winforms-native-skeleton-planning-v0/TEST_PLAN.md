# Test Plan

Planning-time validation:

- `python scripts/validate_windows_winforms_skeleton_plan.py`
- `python scripts/validate_windows_winforms_skeleton_plan.py --json`
- `python -m unittest tests.operations.test_windows_winforms_skeleton_planning tests.scripts.test_validate_windows_winforms_skeleton_plan`

Future skeleton validation, if explicitly approved later:

- verify project path and namespace match the plan
- verify x64 and .NET Framework 4.8 target
- verify no network calls are present
- verify no download/install/cache/telemetry/relay/live-probe controls exist
- verify only allowed static data and seed snapshot inputs are read
- verify missing input files fail closed
- verify no private path examples or absolute local paths are committed
- verify no Rust FFI or Python runtime embedding is introduced

This milestone only adds planning-time validation.

