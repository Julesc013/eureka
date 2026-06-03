# Decisions, Open Questions, and Next Steps — Eureka Workbench and Internet Archive Pilot

_Date anchor used for this report: 2026-05-31 Australia/Melbourne, per user instruction._

## Decisions

### Make Local Appliance the execution harness

Status: final within this chat.

Who accepted it: user accepted by repeatedly requesting prompts and reporting task completions.

Rationale: Future work needed a real local runtime, HTML page, instance layout, WorkUnit queue, review/rebuild flow, and smoke tests instead of more static planning.

Consequences: Product tasks should prove behavior through the local workbench when applicable.

Revisit conditions: only if the project explicitly abandons local-first development, which this chat does not support.

### Use sibling local instances outside the repo

Status: final within this chat.

Who accepted it: user explicitly moved `eureka-instance` beside the repo and preferred separating instance and code.

Rationale: Avoid mutable runtime state polluting source control.

Consequences: Preferred path is `../instances/default`; legacy `../eureka-instance` remains explicit.

Revisit conditions: if packaging/installer requirements require a different default, but source and mutable state should remain separate.

### Complete PLAY before relying on real source behavior

Status: completed within visible task reports.

Rationale: The local workbench needed known hits, known absences, demo Hunts, demo SearchNeeds, demo WorkUnits, and blocked path examples.

Consequences: SYN and IA work have usable anchors.

Revisit conditions: if PLAY data becomes stale or too narrow.

### Internet Archive metadata is the first source pilot

Status: completed through closeout according to user status.

Rationale: IA metadata can be integrated metadata-first without downloads, making it a strong controlled source-family slice.

Consequences: IA becomes the source pattern for future sources.

Revisit conditions: if repo validation contradicts the pasted status or if IA policy changes externally.

### Keep IA metadata pilot separate from full Archive.org integration

Status: final as a claim boundary.

Rationale: Full IA integration includes collection crawling, file manifests, downloads, Wayback, file contents, and extraction, none of which are proven by metadata pilot.

Consequences: Future work must use tiered IA language.

Revisit conditions: after IA-DEEP/F0 stages are built.

### Make Workbench the internal superset

Status: accepted conceptually, not implemented fully.

Rationale: The Workbench should prove final backend/frontend flows before public/native deployment.

Consequences: Future public and native surfaces should project from shared contracts, not separate logic.

Revisit conditions: if maintaining a single kernel/projection architecture becomes impractical.

### Add Search Interaction Contract

Status: recommended and accepted in conversation, not executed.

Rationale: The project needs formal semantics for full-sentence queries, compiled intent, live runs, lanes, user controls, and feedback.

Consequences: This should guide Workbench and SYN.

Revisit conditions: if a smaller interim Workbench UI is deliberately implemented first with clear debt.

## Open Questions

### Has the IA pilot been promoted to `main`?

Why it matters: Future work should know whether IA closeout is canonical.

Known: user provided IA closeout status on `dev`; assistant suggested promotion review.

Unknown: current actual Git branch state after the chat.

Resolution path: run Git status/fetch/compare and IA-to-main promotion review.

Priority: high.

### What are the remaining broad-lane full-discovery failures?

Why it matters: They may block promotion or future production claims.

Known: IA closeout reported full discovery failures outside the IA lane.

Unknown: exact failure causes and whether they affect Workbench/SYN.

Resolution path: classify failures and add remediation tasks if needed.

Priority: high for promotion, medium for continuing on `dev`.

### What is the exact Workbench route/view contract?

Why it matters: It controls how the internal superset becomes reusable across public/API/native surfaces.

Known: recommended routes and packets were listed.

Unknown: exact schemas, permissions, and implementation order.

Resolution path: WORKBENCH-FOUNDATION-00 and SEARCH-INTERACTION-00.

Priority: high.

### How should IA become user-facing in the Workbench?

Why it matters: Current IA pipeline is script/proof-heavy.

Known: IA-HUNT bridge and result lanes are needed.

Unknown: exact polling/event implementation and UI model.

Resolution path: Workbench result lanes/events and IA-HUNT bridge tasks.

Priority: high.

### When can operator instance writes be enabled?

Why it matters: Current writes are temp-instance-only.

Known: operator instance mutation is blocked by default.

Unknown: backup/rollback/apply-gate design.

Resolution path: LOCAL-APPLY gate tasks.

Priority: medium-high.

## Next Steps

### IA-TO-MAIN-PROMOTION-REVIEW

Priority: high.

Dependencies: clean dev, pushed IA closeout, passing IA validators, classified broad-lane failures.

Expected output: promotion review and, if safe, canonical main baseline.

First action: inspect Git branch state.

### REPO-LAYOUT-CANON-00

Priority: high.

Dependencies: current tracked tree inventory.

Expected output: layout contracts, root allowlist, naming policy, generated-state policy, validators.

First action: create tracked-only inventory and root classification.

### WORKBENCH-FOUNDATION-00

Priority: high.

Dependencies: repo layout direction or at least no conflicting root changes.

Expected output: Workbench doctrine, route/view matrix, permission matrix, projection matrix.

First action: define Workbench as internal superset in docs/contracts.

### SEARCH-INTERACTION-00

Priority: high.

Dependencies: Workbench Foundation or parallel contract path.

Expected output: search interaction packets, ResolutionRun state machine, control commands, feedback events.

First action: define packet inventory and state machine.

### IA-HUNT-BRIDGE

Priority: high after interaction contracts.

Dependencies: IA pilot, HUNT, Workbench result lanes/events.

Expected output: query miss to IA WorkUnit, candidate lanes, review bridge, rebuild flow.

First action: define IA WorkUnit contract and Workbench lane mapping.

### SYN-00

Priority: high after Workbench/Interaction, or acceptable after promotion if kept planning-only.

Dependencies: Local/HUNT/PLAY/IA baseline.

Expected output: synthetic query taxonomy, eval contracts, seed datasets, contamination guard.

First action: define query families and non-fake-evidence doctrine.

## Rejected or Deferred Options

### Direct F0 extraction next

Why not carried forward: extraction needs Workbench, source/evidence/review flow, and safety gates.

Can return later: yes, after SYN/DOMAIN/SCOUT foundations.

### Full IA crawling now

Why not carried forward: unsafe, too broad, not rate/budget/review controlled.

Can return later: only as progressive metadata/file/frontier WorkUnits, not uncontrolled crawling.

### Downloads and file fetching now

Why not carried forward: rights, malware, resource, and safety risks.

Can return later: after policy, quarantine, F0, and action safety work.

### Public hosting now

Why not carried forward: production ops/security/rate/abuse/observability not ready.

Can return later: after Workbench, SYN, source quality, and E-track readiness.

### Native/marketplace apps now

Why not carried forward: require stable contracts, snapshots/relay, action policies, and trust systems.

Can return later: much later after core search/resolution engine matures.
