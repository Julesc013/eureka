# Golden Tasks

## Added Tasks

- `repo_boundary_golden`: checks AGENTS boundary doctrine and ensures AIDE-only
  task packets keep Eureka product/runtime paths forbidden.
- `compact_task_packet_golden`: checks the latest task packet has required
  sections, Eureka refs, validation commands, queue/evidence output, and token
  budget discipline.
- `evidence_review_packet_golden`: checks review packets reference task,
  context, verifier, and evidence surfaces without raw prompts, raw responses,
  provider keys, or full dumps.
- `no_secret_or_local_state_golden`: checks `.aide.local/`, `.env`, caches,
  tracked local state, selected packet/report secret scans, and raw body
  absence.
- `eureka_architecture_context_golden`: checks AGENTS, repo map, context packet,
  and architecture validation refs expose Eureka boundaries.
- `generated_agent_guidance_golden`: checks AGENTS managed guidance is current,
  deterministic, compact, and aligned with Eureka AIDE Lite rules.

## Result

- `py -3 .aide/scripts/aide_lite.py eval list`: 12 active tasks.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 12/12.

## What This Proves

- AIDE Lite can validate Eureka-specific governance and packet-readiness
  constraints without giant prompt history.
- The target repo can run deterministic AIDE quality gates before product work.
- The checks are repo-local and do not require providers, models, networks,
  exact tokenizers, or LLM judges.

## What This Does Not Prove

- Arbitrary Eureka implementation quality.
- Exact tokenizer or provider billing savings.
- Product runtime, connector, gateway, native, or surface readiness.
