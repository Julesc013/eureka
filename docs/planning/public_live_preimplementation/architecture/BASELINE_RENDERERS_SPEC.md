# Baseline Renderers Spec

## Minimum Alpha Profiles

- `json_v0`: proves contract shape.
- `text_v0`: proves semantic fallback.
- `html_basic_v0`: proves public browser usability.
- `snapshot_v0`: proves deterministic static/export path.

## Later Profiles

- `html_classic_v0`
- `terminal_v0`
- `native_card_v0`
- `agent_context_v0`
- `relay_v0`

## Required Invariants

All renderers show canonical status, evidence summary, public action posture,
and uncertainty/blocked state. A limited renderer may omit decoration, not
truth posture.

