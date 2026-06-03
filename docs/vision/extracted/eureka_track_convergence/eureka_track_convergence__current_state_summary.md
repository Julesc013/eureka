# Current State Summary — Eureka Track Convergence and Post-P107 Planning

Date anchor: 2026-05-31 Australia/Melbourne. This summary is based only on the visible chat.

## Current State in One Page

At the end of this chat, the Eureka project is being reframed from a long P-number prompt queue into a track-based execution spine. The user introduced `EUREKA-CONVERGE-01 — Track and prompt queue convergence audit` as the current prompt. The stated purpose of that convergence task is to settle the old P-number plan, the current AIDE queue, the Track A/B/D/C/E order, public-alpha reinterpretation, duplicate or obsolete tasks, and the next execution spine. The user gave a conditional outcome model: if convergence passes, start Track A; if it is partial, generate one remediation prompt and then Track A; if it fails, stop and repair convergence or state drift first.

The visible chat also contains pasted reports saying that P107 is complete. Those reports describe a local dry-run public-search ranking runtime with explicit evidence-weighted and compatibility-aware ranking factors, deterministic proposed order, explanations, and fallback behavior. They also state that public search routes, responses, result cards, public ordering, hosted runtime, source cache, evidence ledger, candidate index, public/local/master indexes, telemetry, downloads, uploads, installs, and execution remain unchanged. This archive did not independently verify the repo state; these should be treated as user-provided or previously discussed repo reports unless separately checked.

The user’s new plan puts Track A first after convergence. Track A is the representation and view-model spine. Its purpose is to ensure that standard web, old-browser HTML, text, file-tree, JSON/API, snapshot, relay, and native card outputs share a common public meaning layer. The user’s first proposed Track A task is `TRACK-A-01 — Host/profile/representation contract bundle`.

After Track A, the user’s plan places Manual Observation Batch 0. The reason is that real external baseline observations should feed view-model examples and work-unit examples rather than remaining loose notes. Track B then builds the Eureka Node / contribution / evidence network: needs, work units, nodes, candidates, evidence, review, packs, contribution workflows, safety policies, and dashboards. The first connector pattern after the local loop is Internet Archive metadata only. Track D builds snapshots and relay before native clients. Track C builds native clients as contract/snapshot/relay consumers. Track E handles hosting and operations, with the first hosted product kept modest and honest.

The assistant agreed that the new spine is strong but argued that it misses a control layer before Track A. The proposed addition is Track 0: current-state pointer, P-number-to-track mapping, idempotence/resumption policy, commit/changelog standards, and queue validation. The assistant also recommended adding later tracks for deep extraction, ranking/explanation/search quality, source expansion, packs/federation, actions/preservation, semantic/AI assist, wider clients, and continuous QA. These are recommendations, not user-accepted decisions in the visible chat.

## Settled Points

The user has stated that the new execution plan is based on `EUREKA-CONVERGE-01` followed by Track A, Manual Observation Batch 0, Track B, first IA connector pattern, Track D, Track C, Track E, and later expansion.

Track A’s purpose appears settled: build the representation/view-model spine so future surfaces do not drift semantically.

Manual Observation Batch 0 remains necessary and should be methodologically grounded. The new plan places it after Track A.

The first connector path should be Internet Archive metadata only, not broad crawling or a multi-connector swarm.

Native clients should initially consume snapshots, relay endpoints, manifests, and public envelopes rather than backend internals.

Hosting should begin as the smallest honest public Eureka, not a production overclaim.

## Tentative Points

Track 0 is tentative. It was recommended by the assistant but not visibly accepted by the user after the recommendation.

`TRACK-A-00 — Canonical public record envelope contract` is tentative for the same reason.

Tracks F–L/Q are recommended amendments, not confirmed user decisions.

Exact track numbering may change after `EUREKA-CONVERGE-01` completes.

The degree to which Track E should be delayed until after Track C is strategically chosen by the user’s new plan, but could be revisited if public alpha pressure changes.

## Blocked Points

The result of `EUREKA-CONVERGE-01` is not visible in this chat. Nothing should proceed as if it passed unless the user supplies or confirms that result.

Manual Observation Batch 0 remains unresolved in the visible reports. External baseline comparison remains unsupported until observations exist.

Hosted deployment remains described as failed, unverified, or not configured in the pasted reports. Public hosted claims remain blocked unless separately verified.

Live connector runtime remains approval-gated. Internet Archive metadata should not be probed live until source policy, User-Agent, contact, quota, cache, and kill-switch decisions are made.

Deep extraction runtime remains blocked by sandbox/resource-limit approval according to the visible reports.

Public ranking integration remains blocked by explanation, eval, and safety gates despite P107 dry-run work.

## User Decisions Needed

The user should decide whether Track 0 is accepted as a required insertion before Track A.

The user should decide whether `TRACK-A-00` should precede `TRACK-A-01`.

The user should decide how to map old P-number tasks into the new tracks, or approve a mapping task to do it.

The user should decide when and how Manual Observation Batch 0 will be performed.

The user should decide source policy, User-Agent/contact, quota, and kill-switch posture for the first IA metadata connector.

The user should decide when hosting becomes important enough to move Track E earlier or keep it late.

## Verification Needed

The result of `EUREKA-CONVERGE-01` needs verification.

The repo state described in the pasted P107 and whole-system reports should be verified if used as factual project status.

Hosted deployment status should be rechecked before any public claims.

External baseline counts should be verified after Manual Observation Batch 0.

Any current GitHub, tooling, or deployment facts may be stale unless checked in a future turn.

## Best Next Action

First, obtain or inspect the result of `EUREKA-CONVERGE-01`. If it fails or is partial, repair convergence/state drift as the user specified. If it passes, the safest next action is to create a Track 0-style current-state and queue spine hardening prompt before Track A, or explicitly fold those control requirements into the first Track A prompt.

## Future Assistant Instructions

Do not assume that assistant-recommended Track 0 and Tracks F–L/Q were accepted by the user. Present them as recommended additions unless the user confirms them.

Do not continue the old P108/P109 sequence as if the track plan did not supersede it. Instead, map old P-number work into the new track system.

Do not treat P107 dry-run ranking as public ranking integration.

Do not treat external baseline readiness as completed external comparison.

Do not treat source observations, candidates, packs, or AI output as truth.

Continue from the convergence result, not from a guessed state.
