# Changed Files

## Golden Task Definitions

- `.aide/evals/golden-tasks/catalog.yaml`
- `.aide/evals/golden-tasks/README.md`
- `.aide/evals/golden-tasks/repo_boundary_golden/**`
- `.aide/evals/golden-tasks/compact_task_packet_golden/**`
- `.aide/evals/golden-tasks/evidence_review_packet_golden/**`
- `.aide/evals/golden-tasks/no_secret_or_local_state_golden/**`
- `.aide/evals/golden-tasks/eureka_architecture_context_golden/**`
- `.aide/evals/golden-tasks/generated_agent_guidance_golden/**`

## Runner And Tests

- `.aide/scripts/aide_lite.py`: registered and implemented six
  metadata-only Eureka-specific golden task runners, plus minimal selftest
  fixture markers and safer generated packet defaults.
- `.aide/scripts/tests/test_golden_tasks.py`: added coverage for catalog
  registration, 12-task reports, and each Eureka-specific golden task.

## Generated Artifacts

- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/context/**` and `.aide/reports/**` after final regeneration.

## Memory And Evidence

- `.aide/memory/project-state.md`
- `.aide/memory/open-risks.md`
- `.aide/queue/EUREKA-AIDE-GOLDEN-01/**`

## Explicitly Unchanged

- No Eureka product source files.
- No `runtime/**`, `contracts/**`, `surfaces/**`, `connectors/**`, `crates/**`,
  `packaging/**`, `third_party/**`, or product test changes.
- No `.aide.local/`, `.env`, secrets, raw prompts, or raw responses.
