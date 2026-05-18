# Review Decision Schema

Review decisions include:

- decision id
- review item id
- candidate id
- decision value
- rationale
- reviewer kind
- preview creation flag

Only `approve_for_reviewed_index_dry_run` may create a promotion preview. Every
decision keeps accepted truth, reviewed-index mutation, and master-index
mutation false.

