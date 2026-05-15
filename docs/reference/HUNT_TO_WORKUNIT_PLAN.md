# Hunt-to-WorkUnit Plan

Plan schema: `search_need_workunit_plan.v0`.

Each plan item includes:

- `plan_item_id`
- `kind`
- `title`
- `policy_state`
- `reason`
- `priority`
- disabled execution/source/extraction/model flags
- payload links to SearchNeed, Search Hunt, and exhaustion report

Plan preview does not persist queue records. Persistence is a separate operator-token-gated action.
