# SearchNeed WorkUnit Links

Created WorkUnits carry link fields in payload:

- `search_need_id`
- `search_hunt_id`
- `exhaustion_report_id`
- `generated_from`
- `policy_state`

The WorkUnit queue payload reference table also records `search_need`, `search_hunt`, and `exhaustion_report` references.

These links are local runtime state only. They are not evidence acceptance and do not mutate reviewed or master indexes.
