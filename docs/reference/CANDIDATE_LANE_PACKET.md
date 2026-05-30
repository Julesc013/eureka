# Candidate Lane Packet

`candidate_lane_packet.v0` projects candidate search results into a lane for
public or operator surfaces.

Public profile:

```text
allowed: inspect, view_source, view_provenance, read
blocked: accept, reject, promote, download, extract, execute, upload
truth_status: candidate_only
accepted_truth: false
```

Operator profile can request a review handoff, but promotion remains a separate
review-gated workflow.
