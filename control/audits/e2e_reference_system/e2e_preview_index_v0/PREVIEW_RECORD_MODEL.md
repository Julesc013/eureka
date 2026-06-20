# Preview Record Model

Preview records use schema version `eureka.e2e_preview_record.v0`.

Required concepts:

- stable `preview_record_id`;
- `status`;
- `authority`;
- `semantic_type`;
- title, summary, normalized search text;
- source, evidence, candidate, run, workunit, review, and reviewed-record refs;
- why matched and why ranked;
- uncertainty and missing information;
- permitted and forbidden actions;
- explicit `accepted_truth` and `artifact_verified` flags.

Only reviewed-record authority may carry `accepted_truth: true`.
