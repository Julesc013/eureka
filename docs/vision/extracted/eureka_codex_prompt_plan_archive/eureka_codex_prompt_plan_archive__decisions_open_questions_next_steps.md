# Decisions, Open Questions, and Next Steps — Eureka Codex Prompt Plan and Production Roadmap

Date anchor: 2026-05-31 Australia/Melbourne

## Decisions

### Eureka is an evidence-first temporal object resolver

Status: final within this chat.

Accepted by: The user continued the conversation on this basis; the assistant repeatedly used it as the organizing doctrine.

Rationale: Archive/software search has high uncertainty around identity, source, compatibility, rights, safety, and availability. An evidence-first resolver can preserve uncertainty and explain provenance rather than returning overconfident answers.

Consequences: Every major subsystem must preserve source/evidence/provenance, limitations, risk, and review status. AI, source cache, evidence ledger, candidates, and ranking cannot be treated as truth.

Revisit conditions: Only if the project’s core mission changes.

### Public search must remain bounded and not perform live fanout

Status: final for near-term alpha.

Accepted by: Reflected throughout generated prompts.

Rationale: Live source fanout creates source-policy, rate-limit, arbitrary URL, privacy, and false-confidence risks.

Consequences: Public search should read the controlled local/public index first. Connectors feed source cache/evidence via source-sync workers, not public query paths.

Revisit conditions: After connector runtimes, cache/evidence storage, review, and public safety gates are approved.

### Dry-run runtimes precede authoritative runtimes

Status: final for near-term plan.

Accepted by: Reflected in P98–P107 and final roadmap.

Rationale: Dry-runs allow implementation and testing of loaders, classifiers, validators, renderers, reports, and factor systems without mutation.

Consequences: Future assistants must not treat dry-run reports as source cache, evidence ledger, page runtime, pack import, or ranking production behavior.

Revisit conditions: After dry-run systems pass audits and authoritative local storage policies are approved.

### Blockers should be resolved autonomously where safe

Status: final user correction.

Accepted by: User explicitly corrected the prompt-writing strategy.

Rationale: Codex should act as a clean-room developer with enough context to resolve normal blockers without repeated human questions.

Consequences: Prompts include blocker classification, safe repair guidance, prohibitions, verification commands, and final reports.

Revisit conditions: If a future agent causes damage or oversteps because prompts are too permissive.

### Manual Observation Batch 0 is human-operated

Status: final.

Accepted by: Reflected in P102 and prior baseline planning.

Rationale: External baseline observations require actually observing external systems. Codex must not fabricate those results.

Consequences: External comparison and superiority claims remain blocked until valid human records exist.

Revisit conditions: None for fabrication; automation may assist validation, not observation, unless separately approved.

### Stop indefinite prompt expansion after P107 and consolidate

Status: recommendation, not explicitly accepted in the visible chat.

Accepted by: Not yet clearly accepted by user in visible transcript.

Rationale: The architecture has enough breadth; execution needs to catch up.

Consequences: Best next move is to execute P96–P107, then audit before generating large new ranges.

Revisit conditions: User may choose to continue generating prompts, but risk of roadmap sprawl increases.

## Open Questions

### What is the actual live repository state?

Why it matters: The prompt queue is generated through P107, but the user says the repo is around P95. Future work depends on knowing what has landed.

Known: User stated live repo is around P95.

Unknown: Exact commits, files, tests, and whether later prompts have been executed elsewhere.

Resolution path: Run a repo audit or inspect Git history and command matrix.

Priority: Critical.

### Is hosted public search deployed and verified?

Why it matters: Public alpha and hosted runtime paths depend on it.

Known: Earlier summaries treated hosted deployment as operator-gated or unverified.

Unknown: Current backend URL, route status, edge/rate limits, health checks, and deployment evidence.

Resolution path: Run hosted deployment verification scripts and inspect P77 or later evidence.

Priority: Critical for public alpha.

### Has Manual Observation Batch 0 been completed?

Why it matters: External baseline comparison and quality claims depend on human observations.

Known: The plan treats it as human-operated and likely pending.

Unknown: Current observed/pending/invalid counts.

Resolution path: Run baseline status scripts and inspect observation records.

Priority: High.

### Which connector should be approved first?

Why it matters: The first connector sets the runtime pattern for all later live source work.

Known: Assistant recommended Internet Archive metadata as likely first path.

Unknown: User/operator decision and source-policy approval.

Resolution path: Human/operator review of connector approval packs and source policies.

Priority: High after public alpha basics.

### What authoritative storage should source cache and evidence ledger use?

Why it matters: Dry-runs do not provide durable runtime state.

Known: Authoritative runtime planning is proposed after P107.

Unknown: Storage format, migrations, rollback, retention, and review workflow.

Resolution path: P108/P109 or equivalent planning prompts.

Priority: High.

## Next Steps

### Execute or verify P96–P107

Priority: Critical.

Dependencies: Live repo state around P95 must be verified.

Expected output: Search explanation contract, dry-run source/evidence/page/pack/ranking runtimes, integration audits, connector audit, manual observation follow-up.

First action: Inspect Git history and run current validators to determine which prompts have landed.

### Run a consolidation audit after P107

Priority: Critical.

Dependencies: P96–P107 execution.

Expected output: Actual state matrix comparing contracts, planning, dry-runs, public search, hosted deployment, connectors, pages, ranking, and baselines.

First action: Generate a P108 or consolidation prompt if P107 is live.

### Plan authoritative local source cache and evidence ledger

Priority: High.

Dependencies: P98/P99 dry-runs and consolidation audit.

Expected output: Storage, migration, rollback, review, and mutation policy plans.

First action: Create P108/P109 prompts or equivalent.

### Harden public alpha

Priority: High.

Dependencies: Hosted deployment evidence, public search safety, static handoff, privacy/security docs.

Expected output: Live alpha readiness evidence and rollback plan.

First action: Verify P77/P58/P57 status and current backend deployment.

### Complete Manual Observation Batch 0

Priority: High.

Dependencies: Human/operator work.

Expected output: Valid external baseline observation records and comparison eligibility.

First action: Use P102 worksheet and validator if implemented.

## Rejected or Deferred Options

### Direct live connector fanout from public search

Why not carried forward: Unsafe source policy, rate-limit, arbitrary URL, and truth-boundary risks.

Can return later: Only through approved source-sync/cache/evidence/review path.

### AI/model answer generation

Why not carried forward: Would risk hallucinated truth and hidden reasoning before evidence systems are mature.

Can return later: As typed candidate assistance after deterministic retrieval and review gates.

### Downloads, installs, execution, package managers, emulators, VMs

Why not carried forward: Rights, malware, safety, compatibility, and execution risks.

Can return later: Only after action policy, sandboxing, rights/risk review, and explicit user/operator approval.

### Public contribution intake

Why not carried forward: Abuse, spam, poisoning, rights, privacy, and moderation risks.

Can return later: After pack quarantine, review queues, storage policy, abuse policy, and moderation workflow.

### Continuing prompt generation indefinitely

Why not carried forward: Risks roadmap sprawl and divergence from repo reality.

Can return later: After execution and consolidation.
