# Prompt

Implement `EUREKA-AIDE-GOLDEN-01 - Add Eureka-specific AIDE golden tasks`.

Use `.aide/context/latest-task-packet.md` as primary context. Add deterministic
repo-local golden tasks for:

- `repo_boundary_golden`
- `compact_task_packet_golden`
- `evidence_review_packet_golden`
- `no_secret_or_local_state_golden`
- `eureka_architecture_context_golden`
- `generated_agent_guidance_golden`

Do not change Eureka product behavior. Keep changes in AIDE Lite eval, test,
context, report, memory, and queue evidence paths. Run validation and stop at
review.
