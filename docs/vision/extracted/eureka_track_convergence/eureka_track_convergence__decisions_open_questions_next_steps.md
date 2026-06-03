# Decisions, Open Questions, and Next Steps — Eureka Track Convergence and Post-P107 Planning

## Decisions

### Decision 1 — Move from P-number queue toward track-based execution

Status: final as a user-stated plan, subject to `EUREKA-CONVERGE-01` outcome.

Who accepted it: the user stated it as “This is the new plan.”

Rationale: the project had accumulated a long P-number queue and needed a clearer execution spine.

Consequences: future work should not blindly continue P108–P170 as the primary structure. Old P-number work should be mapped into the new tracks.

Revisit conditions: if `EUREKA-CONVERGE-01` fails or reveals unresolved drift.

### Decision 2 — Use `EUREKA-CONVERGE-01` as the gate before next work

Status: final within the visible user plan.

Who accepted it: user.

Rationale: convergence must settle old plan, current queue, track order, obsolete tasks, and public-alpha reinterpretation.

Consequences: next action depends on PASS/PARTIAL/FAIL.

Revisit conditions: if the convergence prompt cannot produce the expected outputs or if the repo state has changed substantially.

### Decision 3 — Track A is the representation/view-model spine

Status: final within the visible user plan.

Who accepted it: user; assistant agreed with the principle.

Rationale: every public surface needs shared meaning: web, old-browser HTML, text, files, API, snapshot, relay, native cards.

Consequences: Track A precedes most product surface work.

Revisit conditions: only if a minimal control task is inserted before Track A, as the assistant recommended.

### Decision 4 — Manual Observation Batch 0 follows Track A

Status: final within the visible user plan.

Who accepted it: user.

Rationale: observations should feed view-model examples and work-unit examples.

Consequences: external baseline grounding is delayed until after representation contracts, but should be more structured when done.

Revisit conditions: if external baseline truth becomes urgent enough to run in parallel.

### Decision 5 — Track B builds the node/contribution/evidence network

Status: final within the visible user plan.

Who accepted it: user; assistant recommended amendments.

Rationale: Eureka needs a learning loop from search needs through candidates, evidence, review, and improved search.

Consequences: source/evidence runtime planning and contribution workflows should live here.

Revisit conditions: if Track B becomes too broad and needs subtracks.

### Decision 6 — First connector pattern starts with Internet Archive metadata only

Status: final within visible user plan.

Who accepted it: user.

Rationale: IA metadata is central and lower risk than downloads or broad scraping.

Consequences: other connectors wait until the IA pattern is proven.

Revisit conditions: if IA source policy or technical constraints block the path.

### Decision 7 — Track D snapshot/relay comes before Track C native clients

Status: final within visible user plan.

Who accepted it: user; assistant agreed.

Rationale: native clients should consume stable snapshots/relay/manifests, not backend internals.

Consequences: native work is read-only and compatibility-driven at first.

Revisit conditions: if a native proof is needed earlier, it should remain a fixture/protocol proof only.

### Decision 8 — Track E hosting comes after representation/contribution/relay/native boundaries

Status: final within visible user plan, but strategically revisitable.

Who accepted it: user.

Rationale: hosted public Eureka should not launch before core public meaning and consumption boundaries are coherent.

Consequences: public alpha may be delayed, though an early static sanity check remains possible.

Revisit conditions: if a minimal static or hosted local-index alpha becomes urgent.

### Decision 9 — Add Track 0 before Track A

Status: tentative assistant recommendation.

Who accepted it: assistant recommended; user has not visibly accepted.

Rationale: changing execution models requires current-state pointer, mapping, idempotence, and queue policy.

Consequences: immediate next task would be Track 0 rather than Track A.

Revisit conditions: user confirms or rejects it; convergence outputs may already satisfy it.

### Decision 10 — Add later Tracks F–L/Q

Status: tentative assistant recommendation.

Who accepted it: assistant recommended; user has not visibly accepted.

Rationale: deep extraction, ranking/explanation, source expansion, federation, actions, AI, wider clients, and QA should not be lost.

Consequences: these domains get named but remain later/gated.

Revisit conditions: user accepts, modifies, or asks for a shorter plan.

## Open Questions

### Question 1 — Did `EUREKA-CONVERGE-01` pass?

Why it matters: it determines the next action.

Known: user described the gate logic.

Unknown: actual result.

Resolution path: inspect or paste convergence completion report.

Priority: highest.

### Question 2 — Should Track 0 be formally inserted before Track A?

Why it matters: it prevents queue drift and duplicate task ambiguity.

Known: assistant recommended it.

Unknown: user acceptance.

Resolution path: user decision or convergence report evidence that equivalent controls already exist.

Priority: high.

### Question 3 — How exactly do P108–P170 map to the new tracks?

Why it matters: avoids losing or duplicating prior planning.

Known: many old tasks correspond to Track B/G/F/etc.

Unknown: complete mapping.

Resolution path: P-number-to-track mapping registry.

Priority: high.

### Question 4 — When will Manual Observation Batch 0 be executed?

Why it matters: external baseline comparison remains unsupported without it.

Known: user wants it after Track A.

Unknown: who executes it and when.

Resolution path: OBS0 protocol and execution packet.

Priority: high.

### Question 5 — What is the current verified hosted deployment state?

Why it matters: public hosted claims depend on it.

Known: visible reports said failed/unverified/not configured.

Unknown: current actual state.

Resolution path: operator verification.

Priority: medium-high.

### Question 6 — What source policy applies to the first IA metadata probe?

Why it matters: live connectors require rate, User-Agent, contact, quota, and kill-switch decisions.

Known: IA metadata is the first connector pattern.

Unknown: exact policy.

Resolution path: source policy decision prompt.

Priority: high before connector runtime.

### Question 7 — What sandbox/resource limits unblock deep extraction?

Why it matters: extraction is essential but risky.

Known: visible reports say deep extraction runtime is blocked by missing policy.

Unknown: approved limits and sandbox design.

Resolution path: Track F sandbox approval.

Priority: later but important.

## Next Steps

### Step 1 — Determine convergence result

Priority: highest.

Dependencies: output of `EUREKA-CONVERGE-01`.

Expected output: pass/partial/fail status and convergence artifacts.

First action: ask for or inspect the convergence completion report.

### Step 2 — If pass, create Track 0 or equivalent state controls

Priority: high.

Dependencies: convergence pass or partial remediation.

Expected output: current-state pointer, track map, idempotence/resumption policy, queue validator.

First action: generate `TRACK-0-01` prompt or fold controls into the next convergence remediation.

### Step 3 — Begin Track A canonical representation work

Priority: high.

Dependencies: convergence pass and preferably Track 0 controls.

Expected output: canonical public envelope, representation profiles, renderer parity framework.

First action: generate `TRACK-A-00` or `TRACK-A-01`.

### Step 4 — Prepare Manual Observation Batch 0 protocol

Priority: high after initial Track A.

Dependencies: view-model fields sufficiently defined.

Expected output: observation protocol, recording templates, anti-fabrication checklist.

First action: generate `OBS0-00` or `OBS0-01`.

### Step 5 — Start Track B local learning loop

Priority: high after Track A/OBS0 setup.

Dependencies: representation and observation artifacts.

Expected output: node, need, work unit, candidate, source/evidence, review, and pack workflows.

First action: generate Track B opening prompt with source/evidence terminology decision.

## Rejected or Deferred Options

### Option — Continue old P108 directly

Why not carried forward: the user introduced a new track-based plan.

Can it return later: yes, as mapped Track B source-cache/evidence planning.

### Option — Jump directly to hosted public alpha

Why not carried forward: new plan puts representation, contribution/evidence, snapshot/relay, and native-consumption boundaries first.

Can it return later: yes, as Track E or early static sanity check.

### Option — Implement all connectors at once

Why not carried forward: unsafe and too broad.

Can it return later: only one connector pattern at a time after IA proves the model.

### Option — Public ranking integration after P107

Why not carried forward: P107 is dry-run only; public ranking needs explanation and eval gates.

Can it return later: yes, in Track G.

### Option — Deep extraction runtime now

Why not carried forward: sandbox/resource approval missing.

Can it return later: yes, in Track F.

### Option — AI runtime now

Why not carried forward: AI remains optional, late, and non-authoritative.

Can it return later: yes, in Track K.
