# AI Escalation Gate Record

AI escalation gate records use schema `ai_escalation_gate.v0`.

Required fields include:

- `gate_id`
- `search_hunt_id`
- `search_need_id`
- `exhaustion_report_id`
- `agent_research_task_id`
- `query`
- `normalized_query`
- `state`
- `eligibility`
- `input_packet`
- `output_classes`
- `forbidden_actions`
- `provider_enabled: false`
- `execution_enabled: false`
- `candidate_only_output: true`
- `review_required: true`
- `created_at`
- `updated_at`

Gate states are `disabled_by_default`, `eligible_but_disabled`, `blocked_missing_exhaustion_report`, `blocked_missing_search_need`, `blocked_by_policy`, `waiting_for_operator_approval`, `waiting_for_provider_gate`, `cancelled`, and `superseded`.
