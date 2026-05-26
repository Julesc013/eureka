# Test Lane Policy

Per-commit default:

- `L0_static_preflight`
- `L1_focused_unit`
- selected `L2_impact_integration`

Promotion default:

- `L0_static_preflight`
- `L1_focused_unit`
- `L2_impact_integration`
- `L3_full_discovery`
- `L4_promotion_release`

L3 full discovery runs through `python scripts/run_full_unittest_discovery.py`
or the `Full Discovery` GitHub Actions workflow. It captures stdout, stderr,
exit code, environment, failure families, failed tests, and a compact JSON
summary before Codex/AIDE reads the result.

Skips are allowed only when the selector records why the skipped command does
not own the changed subsystem and no active known failure requires it.

Skips are not allowed for promotion full discovery, recent failures, touched
contracts, touched runtime code, persistence or migration changes, architecture
boundaries, or generated artifact cleanliness.

Fake green is forbidden: a task may report selected-lane success, but it must
also report any deferred full discovery and known failure ledger state.

AI-assisted edits should not run `python -m unittest discover -s tests -t .`
interactively. If full discovery is required, use the harness or CI artifact
path and report only the compact summary.

