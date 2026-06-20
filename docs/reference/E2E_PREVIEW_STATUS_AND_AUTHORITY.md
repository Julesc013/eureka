# E2E Preview Status and Authority

The E2E Preview Index uses separate fields for result status and authority.
Status describes what kind of result the operator is seeing. Authority describes
why Eureka is allowed to show it and what it must not imply.

## Statuses

- `reviewed`: local reviewed record input with explicit review lineage.
- `candidate`: provisional candidate, run projection, or source-derived lead.
- `near_miss`: related item that fails a material query constraint.
- `need`: unresolved work or insufficient support.
- `absence`: absence or missing-source finding.
- `policy_blocked`: result exists only as a blocked action or policy state.
- `unavailable`: source or run material was unavailable.
- `unknown`: retained state whose type is not yet classified.
- `mention_only`: source or evidence mention that is useful for context only.
- `superseded`: older preview record retained for lineage.
- `rejected`: rejected preview material, hidden by default.
- `private_local`: private local overlay material, hidden unless explicitly used.

## Authorities

- `reviewed_record`: accepted local reviewed-record input with review refs.
- `candidate_only`: candidate delta input; never accepted truth.
- `source_observation_only`: source observation input; not reviewed truth.
- `evidence_summary_only`: evidence summary input; support material only.
- `absence_finding`: absence or near-miss support material.
- `run_projection`: non-synthetic ResolutionRun lane projection.
- `synthetic_test`: isolated synthetic/replay material.
- `unknown`: retained but untrusted preview material.

Only `reviewed_record` authority may set `accepted_truth: true`. A preview
record with candidate, source-observation, evidence-summary, absence, run, or
synthetic authority must remain non-authoritative.

The Preview Index itself is derived, rebuildable, and reversible. It does not
create reviewed records, refresh reviewed/master indexes, mutate public indexes,
or publish snapshots.
