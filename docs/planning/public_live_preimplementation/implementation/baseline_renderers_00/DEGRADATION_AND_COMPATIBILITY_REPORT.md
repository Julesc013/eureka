# Degradation And Compatibility Report

Task ID: `BASELINE-RENDERERS-00`

## Status Handling

Renderer tests prove these states remain visible:

```text
candidate
need
policy_blocked
unavailable
unknown
```

Fallback-derived states are not converted to `verified`.

## Unsupported Profiles

Unsupported profile requests continue through SurfaceKernel capability negotiation and fall back to:

```text
html_basic_v0
```

The renderer dispatch then uses:

```text
surface_html_basic_v0
```

## HTML Safety

`html_basic_v0` escapes fields used for:

```text
title
summary
status
fallback status
reason codes
candidate labels
need labels
action ids
policy notes
```

Focused tests prove unsafe text is escaped rather than emitted raw.

## Snapshot Determinism

`snapshot_v0` emits a stable dict with sorted action ids and policy notes plus a deterministic digest over the policy-filtered view model.

Focused tests prove repeated rendering of the same SurfaceKernel request produces identical snapshot output and cache metadata.
