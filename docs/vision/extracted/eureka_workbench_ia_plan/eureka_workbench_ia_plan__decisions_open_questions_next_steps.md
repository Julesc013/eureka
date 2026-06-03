# Decisions, Open Questions, and Next Steps — Eureka Workbench, IA Connector, and Production Path

## Decisions

### Structured commits and resumable WorkUnits

Status: accepted in practice, though implementation state must be verified.

Who accepted it: The user pushed for better commit format; assistant proposed the structure; subsequent prompts used it.

Rationale: Commits should be readable at a glance and compile into changelogs/release notes. WorkUnits should recover from duplicate, stale, repeated, or out-of-order prompts.

Consequences: Future commits should use Conventional Commit subjects, structured Markdown bodies, validation sections, changelog categories, trailers, and WorkUnit recovery metadata.

Revisit conditions: If the format becomes too heavy or tooling fails to enforce it.

### Prompt ID-first headers

Status: final for generated prompts in this chat.

Who accepted it: User explicitly required it.

Rationale: The queue needed easy identification and ordering.

Consequences: Future generated prompts should begin with the task ID and include track, timestamp, title, and summary.

Revisit conditions: Only if the project adopts a different prompt orchestration system.

### Manual observations should be agent-assisted

Status: accepted direction.

Who accepted it: User rejected manually performing bulk observations and wanted agents/subagents to generate candidates for approval.

Rationale: Human time is limited; agents can gather candidates, but humans approve/reject.

Consequences: Observation tracks should use review queues and anti-fabrication rules.

Revisit conditions: If source policy or quality issues make agent observations unreliable.

### H-series scaffolding is not product implementation

Status: accepted as a corrective principle.

Who accepted it: Assistant agreed with user’s critique of the messy branch.

Rationale: Contracts, policies, validators, and audit packs do not prove runtime behavior.

Consequences: Future tasks must prove real product capabilities with behavior and integration tests.

Revisit conditions: None for the principle; specific classifications may change after repository audit.

### PLAY → IA → SYN → DOMAIN → SCOUT → F ramp

Status: strong proposed plan.

Who accepted it: User presented this synthesis and asked for reaction; assistant agreed. Explicit final user confirmation after that is not visible.

Rationale: PLAY anchors usability, IA proves a real source, SYN adds pressure, DOMAIN generalizes, SCOUT discovers relations, F finds hidden members.

Consequences: Do not run broad source expansion or F extraction too early.

Revisit conditions: If the current repo state or user priorities shift.

### Workbench as internal superset

Status: strong proposed doctrine; likely aligned with user intent, but future implementation should confirm.

Who accepted it: User proposed the framing; assistant agreed.

Rationale: The Workbench should prove backend features, UI patterns, review flows, source connectors, and safety boundaries before public or native projections.

Consequences: Future backend features need Workbench views and shared packets.

Revisit conditions: If a separate UI architecture is chosen, though that would risk semantic drift.

## Open Questions

### Has IA been promoted from dev to main?

Why it matters: Workbench and SYN should start from canonical baseline if possible.

Known: Visible chat reports dev ahead of main by 22 commits after IA pilot.

Unknown: Whether promotion occurred after the final visible repo check.

Resolution path: Recheck branch comparison and health files.

Priority: High.

### Should Workbench Foundation precede SYN-00?

Why it matters: Repo health recommended SYN, but final product plan recommended Workbench first.

Known: SYN is safe/planning-only; Workbench would give SYN visible behavior to test.

Unknown: User’s final implementation choice.

Resolution path: Ask user or inspect updated queue.

Priority: High.

### How permanent is the IA vertical slice?

Why it matters: Some IA writes were temp explicit instance proofs; production persistence may still be incomplete.

Known: Health reported IA source-cache, evidence, candidate, review, and index stages passed in temp/explicit scope.

Unknown: Which pieces are durable runtime versus proof artifacts.

Resolution path: Inspect runtime, scripts, instance store, and tests.

Priority: High.

### What packet types should be canonical?

Why it matters: Workbench/public/native projections need shared packets.

Known: Proposed packet families include SearchResultPacket, HuntStatePacket, CandidatePacket, EvidencePacket, ReviewPacket, SourceRecordPacket, IndexRebuildPacket, AbsencePacket, ActionPosturePacket.

Unknown: Actual contract names and schemas.

Resolution path: WORKBENCH-FOUNDATION-00.

Priority: Medium-high.

### When should broader source expansion resume?

Why it matters: Too many connectors too early caused risk.

Known: IA should be first; next candidates include GitHub Releases, package registries, Software Heritage, Wayback/CDX, Open Library/Wikidata.

Unknown: Exact second source after IA.

Resolution path: After Workbench/SYN results.

Priority: Medium.

## Next Steps

### Reverify current branch state

Priority: High.

Dependencies: GitHub/local repo access.

Expected output: Confirm whether dev and main are aligned, current recommended queue item, IA promotion status, and health.

First action: Compare `main` and `dev`, fetch `.aide/reports/eureka-repo-health.json`.

### IA-TO-MAIN-PROMOTION-REVIEW

Priority: High if IA is still dev-only.

Dependencies: IA pilot validation and clean promotion gates.

Expected output: Canonical main branch with IA pilot baseline.

First action: Run promotion review task.

### WORKBENCH-FOUNDATION-00

Priority: High.

Dependencies: Branch baseline chosen.

Expected output: Workbench doctrine, route/view/API matrix, packet policy, permissions, projection model.

First action: Generate/execute a focused Codex prompt.

### WORKBENCH-RESULT-LANES-01

Priority: High after foundation.

Dependencies: Workbench route/packet model.

Expected output: Lane model for reviewed results, candidates, source cache hits, IA candidates, review items, absence, blocked actions, running WorkUnits.

First action: Define lane packets and local HTML projection.

### WORKBENCH-EVENTS-02

Priority: Medium-high.

Dependencies: Hunt/search/job model.

Expected output: Polling endpoints and event packets for progressive search/Hunt.

First action: Implement polling rather than WebSockets.

### IA-HUNT-BRIDGE-00 and IA-HUNT-WORKUNIT-01

Priority: High after lanes/events.

Dependencies: IA pilot and Workbench packet model.

Expected output: Query miss to Hunt/SearchNeed/IA WorkUnit/source observation/evidence/review/index loop.

First action: Define IA metadata WorkUnit and event sequence.

### SYN-00 over Workbench-visible behavior

Priority: High after initial Workbench/IA bridge.

Dependencies: PLAY, HUNT, IA, Workbench lanes.

Expected output: Synthetic query foundry planning over real visible flows.

First action: Reframe SYN-00 around Local/HUNT/PLAY/IA/Workbench.

## Rejected or Deferred Options

### Broad “add all sites now”

Reason not carried forward: It risks source sprawl and returns to scaffold-heavy development without a visible product loop.

Can return later: Yes, after Workbench and SYN discipline source expansion.

### Synchronous all-IA deep search

Reason not carried forward: Too slow, too broad, rate-limit-prone, and unsafe.

Can return later: As demand-driven frontier/deepening jobs, not a blocking page request.

### Public hosted search now

Reason not carried forward: Production operations, reviewed corpus, security, rate limits, observability, and public launch evidence are insufficient.

Can return later: After local Workbench, IA loop, SYN, and ops gates.

### Marketplace/app-manager behavior

Reason not carried forward: Requires high-risk actions, rights, malware, trust, quarantine, install, emulation, and moderation systems.

Can return later: Much later after J/action and safety tracks.

### Direct F extraction now

Reason not carried forward: Extraction is more valuable and safer after Workbench, DOMAIN, SCOUT, and IA-driven WorkUnits.

Can return later: After SYN/DOMAIN/SCOUT or explicit F gates.
