# TRACK-B-10 WorkUnit Dry-Run Runner

This audit pack records the first bounded WorkUnit dry-run runner for Track B.
The runner follows the WorkUnit, WorkUnitResult, node policy, node capability,
local foundry state, search miss, and SearchNeed contracts by simulating only
policy decisions from explicit WorkUnit inputs.

## Added

- `runtime/local/foundry/workunit_dry_run.py`
- `scripts/run_workunit_dry_run.py`
- `scripts/validate_workunit_dry_run_runner.py`
- Dry-run policy, action matrix, output policy, and review policy inventories
- WorkUnit dry-run reference, architecture, and operations docs
- Compact dry-run WorkUnitResult examples
- Generated sample dry-run result and summary under this audit directory

## Boundary

The dry-run runner can validate, classify, and report. It cannot execute
WorkUnits, call networks, call APIs, call models/providers, access live sources,
create private local state, accept candidates, accept evidence, or mutate the
master-index.

## Why This Follows SearchNeed Runtime

TRACK-B-09 introduced reviewable unresolved-search objects. TRACK-B-10 proves
that future SearchNeed-derived WorkUnits can be inspected and simulated before a
real node policy evaluator or runner exists.

## Review And Truth

Every dry-run output is a WorkUnitResult envelope with review gates preserved.
Dry-run results are not public truth, accepted evidence, source validation,
rights clearance, malware safety, verified installability, exhaustive search
proof, production readiness, or master-index permission.

## Validation

See `validation.md` for the command log. The generated sample report was
created from `examples/work_units/search_need_review_v0/work_unit.json`.

## Next

TRACK-B-11 - Node policy evaluator.
