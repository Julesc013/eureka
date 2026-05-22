# Post Workbench Live Run Plan

Recommended next task:

```text
IA-LIVE-METADATA-LANE-01 - Add explicit operator-approved live IA metadata lane
```

Planned after:

- `WORKBENCH-REVIEW-PROMOTE-01`
- `LOCAL-APPLY-GATE-01`
- `SOURCE-WAVE-00`

The next live IA work should use explicit operator approval and should emit run events and lane updates through the same headless kernel seam. It should not wire browser routes directly to IA-specific scripts.
