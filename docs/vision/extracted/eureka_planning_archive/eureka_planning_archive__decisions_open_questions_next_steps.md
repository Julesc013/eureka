# Decisions, Open Questions, and Next Steps — Eureka Planning, AIDE Control, Local Appliance, and Search Hunt Workbench

## Decisions

### Eureka is an evidence-backed resolver, not a generic search engine

Status: final as project doctrine within this chat.

Who accepted it: The user repeatedly carried this framing forward, and later plans rely on it.

Rationale: Normal search does not preserve evidence, provenance, compatibility, rights/risk, absence, candidates, or review state.

Consequences: Every major feature should preserve evidence and uncertainty. Search results should include verified results, candidates, near misses, known absences, and remaining work.

Revisit conditions: Only revisit if the project intentionally narrows into a simpler product, which this chat does not indicate.

### Use one canonical route/object/evidence/action model with many representations

Status: final as architecture doctrine, details still refinable.

Who accepted it: The user continued building plans around capability negotiation and same-system/many-projections.

Rationale: Separate sites/products for eras would fragment truth.

Consequences: Track A/view-model/renderer parity work is foundational. Old clients and native clients consume projections, not separate truth.

Revisit conditions: Specific representation formats can change; the doctrine should not change without explicit architecture review.

### AIDE Lite is the Eureka control layer, not product truth

Status: final.

Who accepted it: The user reported AIDE Lite sync and proceeded with AIDE-driven prompts.

Rationale: AIDE reduces context waste and controls tasks, but generated packets may become stale.

Consequences: Future agents must read AIDE packets but verify live repo state and product contracts.

Revisit conditions: If AIDE becomes tightly integrated with product runtime, this boundary would need review. That is not the current plan.

### Native directories should use API/toolchain names

Status: final for repo structure planning.

Who accepted it: The user asked for short, sharp, long-lived names and continued with the proposed structure.

Rationale: API family names are more stable than “legacy/modern/classic” labels.

Consequences: Native support details belong in matrix files, not paths.

Revisit conditions: Only if a target does not map cleanly to an API/toolchain family.

### Local appliance and Search Hunt Workbench are the product kernel

Status: accepted as current product strategy.

Who accepted it: The user pasted the local appliance fork plan as authoritative and asked for alignment around it.

Rationale: Future tracks need a runnable local product surface, not only contracts.

Consequences: Features should prove behavior through local appliance/workbench where applicable.

Revisit conditions: If the local appliance becomes too heavy or blocks urgent minimal features, but the burden of proof would be on the alternative.

### SYN should not start until branch/AIDE reconciliation is done

Status: current final operational decision.

Who accepted it: Assistant recommendation based on live GitHub evidence; user has not yet reported execution.

Rationale: `main` and `dev` are diverged, main has AIDE eval failures, and generated state is stale.

Consequences: Run `DEV-MAIN-AIDE-SYNC-01` before SYN/F0.

Revisit conditions: If a new live repo check shows branches already reconciled and evals/warnings resolved.

## Open Questions

### How should `main` and `dev` be reconciled?

Why it matters: The branches are diverged 13/13 in the visible GitHub compare.

Known: `dev` has HUNT work and SYN queued; `main` has Q62/AIDE/source-slice state and failing broad golden tasks.

Unknown: Whether merge conflicts exist, whether fast-forward promotion is possible after sync, and how generated files should be regenerated.

Resolution path: Run `DEV-MAIN-AIDE-SYNC-01`.

Priority: highest.

### Can the 9 failing broad AIDE golden tasks be fixed?

Why it matters: AIDE controls future Codex/GPT task quality.

Known: Main’s broad golden run fails 9 of 136 tasks.

Unknown: Whether failures are due to stale state, changed policies, or real defects.

Resolution path: Run `AIDE-EVAL-GREEN-01`.

Priority: high.

### Are HUNT’s six warnings acceptable or fixable?

Why it matters: HUNT is complete with warnings, but promotion review must recheck leakage and generated cleanliness.

Known: Warnings are described as non-blocking for SYN/F0 planning.

Unknown: Their status after branch sync.

Resolution path: Run `HUNT-WARNING-ZERO-01` and `HUNT-PERFECT-CLOSEOUT-01`.

Priority: high.

### Should promotion to `main` happen before SYN?

Why it matters: Continuing on dev might be acceptable, but unreviewed divergence can cause future confusion.

Known: The assistant recommends promotion review before SYN.

Unknown: User/operator preference after sync.

Resolution path: Run `HUNT-TO-MAIN-PROMOTION-REVIEW`.

Priority: high.

### How much of HUNT is runtime-proof versus audit/control surface?

Why it matters: Future SYN/F0 depends on HUNT behavior.

Known: Dev reports HUNT capabilities implemented/tested and workbench smoke passed.

Unknown: Detailed runtime code inspection was not performed in this chat.

Resolution path: HUNT perfect closeout should rerun validators and smoke tests.

Priority: medium-high.

## Next Steps

### DEV-MAIN-AIDE-SYNC-01

Priority: immediate.

Dependencies: Fresh repo state, clean working tree, task-state guard.

Expected output: Dev contains main’s baseline and dev’s HUNT work; AIDE context regenerated; no main mutation yet.

First action: Compare branches and plan merge.

### AIDE-EVAL-GREEN-01

Priority: high.

Dependencies: Branch sync.

Expected output: Broad AIDE golden tasks pass or failures are exactly classified.

First action: Inspect failed golden tasks.

### HUNT-WARNING-ZERO-01

Priority: high.

Dependencies: Branch sync and refreshed AIDE state.

Expected output: Six warnings resolved or explicitly accepted as non-product warnings.

First action: Re-run HUNT/LOCAL checks and warning disposition.

### HUNT-PERFECT-CLOSEOUT-01

Priority: high.

Dependencies: Warning cleanup.

Expected output: Final HUNT state packet under updated AIDE baseline.

First action: Run HUNT/LOCAL validators, smoke tests, cleanliness, leakage, and AIDE checks.

### HUNT-TO-MAIN-PROMOTION-REVIEW

Priority: high.

Dependencies: Perfect closeout.

Expected output: Decision and plan for promoting dev to main.

First action: Compare post-sync dev against main and review audit evidence.

### SYN-00

Priority: next product phase after promotion review.

Dependencies: Sync, eval, warning, closeout, and promotion review gates.

Expected output: Synthetic Query Foundry planning over Local Appliance and Search Hunt.

First action: Read Search Hunt closeout and SYN handoff files.

## Rejected or Deferred Options

### Start SYN immediately

Why not carried forward: Branch divergence and main AIDE failures make immediate SYN risky.

Can return later: Yes, after sync/closeout/promotion review.

### Resume F0 extraction immediately

Why not carried forward: F0 can resume but is not recommended now; SYN should create query/eval pressure first.

Can return later: Yes, after SYN or explicit user override.

### Start public hosting

Why not carried forward: Hosting remains deferred and requires ops/non-claims/rate-limit/log/takedown/launch evidence.

Can return later: Track E.

### Start broad source probes

Why not carried forward: Source probes are disabled and must be policy-gated.

Can return later: Track H after approved source policies and local appliance/HUNT/SYN gates.

### Treat AIDE health reports as authoritative

Why not carried forward: Final branch compare contradicted generated equality claims.

Can return later: AIDE health remains useful after regeneration and validation, but not as sole truth.
