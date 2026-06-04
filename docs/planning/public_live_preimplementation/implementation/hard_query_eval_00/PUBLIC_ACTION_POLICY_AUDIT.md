# Public Action Policy Audit

Task ID: `HARD-QUERY-EVAL-00`

## Public Posture

The hard-query fixtures intentionally include unsafe future/operator action ids in nested allowed-action fixture fields before SurfaceKernel policy filtering.

Focused tests prove public renderer outputs do not expose:

```text
review_candidate
promote
reject
supersede
request_more_evidence
rebuild_index
freeze_review
download
install
launch_emulator
run_extraction
submit_direct_evidence
crawl_source
arbitrary_live_lookup
```

## Allowed Public Actions

Public output remains limited to read-only action ids supplied by SurfaceKernel policy:

```text
view
inspect_evidence
compare
cite
export_manifest
```

## Notes

Fixture block reasons use public-safe wording so blocked/degraded states remain visible without surfacing disallowed action labels as public commands.
