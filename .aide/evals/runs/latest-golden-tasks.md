# Latest Golden Tasks

- result: PASS
- task_count: 14
- pass_count: 14
- warn_count: 0
- fail_count: 0
- provider_or_model_calls: none
- network_calls: none
- raw_prompt_storage: false
- raw_response_storage: false
- token_quality_statement: Token reduction remains valid only if golden tasks pass.

## Tasks

### adapter-managed-section-determinism

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: AGENTS.md
- notes: Checks managed section replacement on an isolated fixture repo.

### commit_message_standard_golden

- result: PASS
- checks_run: 25
- passed_checks: 25
- approx_tokens_if_applicable: n/a
- related_paths: .aide/hooks/commit-msg, .aide/policies/commit-messages.yaml, .aide/reports/eureka-commit-message-standard.md, AGENTS.md
- notes: Checks AIDE enforces changelog-ready commit messages for future work.

### compact-task-packet-required-sections

- result: PASS
- checks_run: 17
- passed_checks: 17
- approx_tokens_if_applicable: 1002
- related_paths: .aide/context/latest-task-packet.md, .aide/policies/token-budget.yaml, .aide/prompts/compact-task.md
- notes: Checks the compact task packet shape and forbidden prompt discipline.

### compact_task_packet_golden

- result: PASS
- checks_run: 32
- passed_checks: 32
- approx_tokens_if_applicable: 1002
- related_paths: .aide/context/latest-context-packet.md, .aide/context/latest-task-packet.md, .aide/context/repo-map.json, .aide/context/test-map.json, AGENTS.md
- notes: Checks the latest compact packet is target-specific and actionable for Eureka.

### context-packet-no-full-repo-dump

- result: PASS
- checks_run: 17
- passed_checks: 17
- approx_tokens_if_applicable: 457
- related_paths: .aide/context/context-index.json, .aide/context/latest-context-packet.md, .aide/context/repo-map.json, .aide/context/test-map.json
- notes: Checks context refs instead of whole-repo dumps.

### eureka_architecture_context_golden

- result: PASS
- checks_run: 30
- passed_checks: 30
- approx_tokens_if_applicable: n/a
- related_paths: .aide/context/latest-context-packet.md, .aide/context/repo-map.json, AGENTS.md, scripts/check_architecture_boundaries.py
- notes: Checks AIDE context surfaces Eureka architecture and validation boundaries.

### evidence_review_packet_golden

- result: PASS
- checks_run: 25
- passed_checks: 25
- approx_tokens_if_applicable: 1247
- related_paths: .aide/context/latest-context-packet.md, .aide/context/latest-review-packet.md, .aide/context/latest-task-packet.md, .aide/verification/latest-verification-report.md
- notes: Checks review packets stay compact, evidence-oriented, and secret-free.

### generated_agent_guidance_golden

- result: PASS
- checks_run: 12
- passed_checks: 12
- approx_tokens_if_applicable: n/a
- related_paths: .aide/adapters/templates/AGENTS.md.template, .aide/generated/adapters/AGENTS.md, AGENTS.md
- notes: Checks generated agent guidance is deterministic, compact, and aligned with Eureka AIDE rules.

### no_secret_or_local_state_golden

- result: PASS
- checks_run: 15
- passed_checks: 15
- approx_tokens_if_applicable: n/a
- related_paths: .aide/context/latest-context-packet.md, .aide/context/latest-review-packet.md, .aide/context/latest-task-packet.md, .aide/evals/golden-tasks/catalog.yaml, .aide/reports/token-savings-summary.md, .gitignore, AGENTS.md
- notes: Checks local state, secret, raw prompt, and raw response boundaries.

### repo_boundary_golden

- result: PASS
- checks_run: 32
- passed_checks: 32
- approx_tokens_if_applicable: n/a
- related_paths: .aide/context/latest-task-packet.md, AGENTS.md
- notes: Checks Eureka product/AIDE boundaries before AIDE-only work is promoted.

### review-packet-evidence-only

- result: PASS
- checks_run: 20
- passed_checks: 20
- approx_tokens_if_applicable: 1247
- related_paths: .aide/context/latest-review-packet.md, .aide/prompts/evidence-review.md, .aide/verification/review-packet.template.md
- notes: Checks review packet evidence-only shape.

### task_resumption_standard_golden

- result: PASS
- checks_run: 28
- passed_checks: 28
- approx_tokens_if_applicable: n/a
- related_paths: .aide/context/latest-task-packet.md, .aide/policies/task-resumption.yaml, .aide/queue/index.yaml, .aide/reports/eureka-task-resumption-standard.md, AGENTS.md
- notes: Checks tasks can be resumed, repeated, or reconciled from repo-local state before asking the user.

### token-ledger-budget-check

- result: PASS
- checks_run: 14
- passed_checks: 14
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/token-ledger.yaml, .aide/reports/token-ledger.jsonl, .aide/reports/token-savings-summary.md
- notes: Checks estimated token metadata without raw prompt or response storage.

### verifier-detects-bad-evidence

- result: PASS
- checks_run: 3
- passed_checks: 3
- approx_tokens_if_applicable: n/a
- related_paths: .aide/evals/golden-tasks/verifier-detects-bad-evidence/fixtures/missing-sections.md, .aide/verification/evidence-packet.template.md
- notes: Passes when the verifier refuses to accept malformed evidence silently.

## Limitations

- Deterministic local checks only.
- No model/provider/network calls.
- No external benchmark or arbitrary code semantic proof.
