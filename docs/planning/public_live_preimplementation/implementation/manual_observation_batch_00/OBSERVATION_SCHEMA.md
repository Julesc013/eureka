# Observation Schema

Task ID: `MANUAL-OBSERVATION-BATCH-00`

Runnable schema-by-example:

```text
evals/hard_queries/manual_observations/batch_00/observations.json
```

Each observation records:

```text
observation_id
query_id
query_text
observer_actor
observation_date
observation_method
source_family
source_reference
source_uri_or_locator
source_access_posture
source_rights_posture
source_risk_posture
object_title_or_label
object_type
platform_or_environment
version_or_date_hint
evidence_summary
evidence_snippets
observed_fields
missing_fields
uncertainty_notes
proposed_status
status_rationale
review_recommendation
review_blockers
public_visibility_posture
allowed_public_actions
forbidden_public_actions
notes
```

Truth-boundary flags are required and must be false:

```text
source_observation_self_promoted
candidate_self_promoted
reviewed_record_created
review_event_created
reviewed_index_mutated
public_index_mutated
master_index_mutated
product_runtime_live_source_call
synthetic_eval_fixture_used_as_evidence
```

The loader validates required fields, canonical statuses, snippet length,
public action posture, and no self-promotion.
