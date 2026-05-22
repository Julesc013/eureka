# Workbench Review Promote API

API payloads use local preview schemas:

- `workbench_review_item.v0`
- `workbench_review_decision.v0`
- `workbench_promotion_preview.v0`
- `workbench_reviewed_index_refresh_preview.v0`
- `workbench_reviewed_index_refresh_temp_result.v0`
- `workbench_review_promote_boundary_report.v0`

Required response posture:

- `operator_token_required: true`
- `automatic_candidate_acceptance_enabled: false`
- `operator_instance_mutated: false`
- `master_index_mutated: false`
- `committed_data_public_index_mutated: false`

The API may expose temp proof output for tests and smoke runs. It must not commit raw local instance state or mutate master/public index artifacts.
