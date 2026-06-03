# Fallback Summary Projection

## Supported States

The Workbench projection exposes:

```text
candidate
need
policy_blocked
unavailable
```

Candidate items are projected as `candidate`, not `verified`.

Need items are projected as `need`.

Policy-blocked fallback state is visible and not review-item creation eligible in this task.

Unavailable fallback state is visible and not review-item creation eligible in this task.

## Source Observation

Source observation summaries are visible to the operator projection and remain non-truth:

```text
verified = false
accepted_truth = false
reviewed_record_created = false
```

Non-operator projections redact source-observation warnings and hide operator actions.

## Review Handoff

Review-item creation is available only for:

```text
candidate
need
```

The handoff creates a sanitized `ReviewItemRecord` from fallback summary fields. It does not write evidence, reviewed records, or indexes.
