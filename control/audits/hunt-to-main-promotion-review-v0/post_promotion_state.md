# Post Promotion State

| Field | Value |
| --- | --- |
| `schema_version` | `"hunt_main_post_promotion_state.v0"` |
| `task` | `"HUNT-TO-MAIN-PROMOTION-REVIEW"` |
| `status` | `"pass"` |
| `post_promotion_verification_required` | `true` |
| `expected_origin_main_equals_origin_dev` | `true` |
| `expected_current_branch_after` | `"dev"` |
| `expected_fast_forward_only` | `true` |
| `origin_main_before` | `"73d8e9eb590f43a5554abe35f99345c57d4ec06c"` |
| `origin_dev_before` | `"be9a23c6a49415fbdceafd03a68555026a77b5bf"` |
| `head_before` | `"c4583b31507aa81fad591ada5d51eb0a9aa72058"` |
| `verification_commands` | `["git rev-parse origin/main", "git rev-parse origin/dev", "git rev-list --left-right --count origin/main...origin/dev", "git status --short --branch"]` |
