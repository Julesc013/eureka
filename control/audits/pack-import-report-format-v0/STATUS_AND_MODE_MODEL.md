# Status And Mode Model

Allowed report statuses are:

- `validate_only_passed`
- `validate_only_failed`
- `partial_validation`
- `unsupported_pack_type`
- `blocked_by_policy`
- `unavailable_validator`
- `future_import_not_performed`

Allowed modes are:

- `validate_only`
- `stage_local_quarantine_future`
- `inspect_staged_future`
- `local_index_candidate_future`
- `contribution_queue_candidate_future`

Only `validate_only` is represented as current example behavior. The other
modes are future labels, not implemented behavior.
