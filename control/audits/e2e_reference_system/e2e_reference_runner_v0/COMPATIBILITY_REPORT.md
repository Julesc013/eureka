# Compatibility Report

Compatibility retained:

- `run_resolution_dry_run(...)` remains available.
- Legacy CLI flags remain available.
- Existing ResolutionRun kernel tests pass.
- Existing ResolutionRun projection tests pass.
- Existing ResolutionRun script tests pass.
- Workbench still consumes the compatibility facade and remains projection-only
  for run lifecycle behavior.

The compatibility facade now delegates through the E2E reference runner.
