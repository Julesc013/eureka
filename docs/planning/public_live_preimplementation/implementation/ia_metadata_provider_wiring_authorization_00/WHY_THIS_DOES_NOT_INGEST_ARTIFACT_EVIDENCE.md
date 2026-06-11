# Why This Does Not Ingest Artifact Evidence

IA metadata provider wiring is not artifact evidence ingestion.

This task may produce:

```text
source_observation
candidate
need
near_miss
policy_blocked
request_more_evidence
unavailable
```

This task must not produce:

```text
reviewed_artifact_record
verified_artifact
artifact_integrity_claim
safe_to_download_claim
rights_cleared_claim
public_truth_claim
```

External artifact evidence remains absent until a separate operator/manual return
provides governed evidence packets.

