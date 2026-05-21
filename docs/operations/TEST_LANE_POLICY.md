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

Skips are allowed only when the selector records why the skipped command does
not own the changed subsystem and no active known failure requires it.

Skips are not allowed for promotion full discovery, recent failures, touched
contracts, touched runtime code, persistence or migration changes, architecture
boundaries, or generated artifact cleanliness.

Fake green is forbidden: a task may report selected-lane success, but it must
also report any deferred full discovery and known failure ledger state.

