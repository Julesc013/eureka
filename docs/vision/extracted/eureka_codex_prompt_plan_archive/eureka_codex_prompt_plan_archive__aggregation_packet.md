# Aggregation Packet — Eureka Codex Prompt Plan and Production Roadmap

Date anchor: 2026-05-31 Australia/Melbourne

## One-Paragraph Summary

This chat records a major Eureka Archive System prompt-generation and roadmap session. The user wanted queueable Codex prompts that would move the repository toward live production while preserving evidence-first architecture, autonomous blocker resolution, Git/AIDE discipline, validation, and no unsafe runtime behavior. The visible prompt queue reaches P107, while the user states the live repository is around P95. The main contribution is a safety-gated sequence from audits and contracts through local dry-run runtimes, authoritative local stores, hosted public alpha, first approved connector, object/source/comparison pages, explanations, ranking, pack import, deep extraction, and eventual clients/offline ecosystem.

## Main Themes

- Evidence-first temporal object resolution rather than generic search or AI answers.
- Clean-room Codex prompt design with autonomous safe blocker resolution.
- Dry-run before runtime and review before mutation.
- Public search must remain bounded and must not perform live source fanout.
- Connector approval is separate from connector runtime.
- Human-operated baseline observations are required before external comparison claims.
- Pages, identity, merge/deduplication, ranking, and explanations make Eureka a resolver product.
- Deep extraction is necessary because wanted objects are often inside containers.

## Major Decisions

- Treat Eureka as an evidence-first resolver.
- Keep public search local/public-index driven until later approval.
- Add contracts and local dry-runs before authoritative runtime.
- Do not let normal blockers stop Codex; prompts must include enough rationale for safe autonomous resolution.
- Keep Manual Observation Batch 0 human-operated.
- Defer AI/model runtime, downloads, installs, uploads, accounts, telemetry, and public contribution intake.

## Major Open Questions

- Exact live repository state relative to generated P107 queue.
- Hosted deployment verification status.
- Manual Observation Batch 0 completion status.
- First connector to approve for live metadata path.
- Authoritative source-cache/evidence-ledger storage policy.
- Whether user accepts the recommendation to pause expansion and execute/consolidate.

## Major Artifacts

- P50 completion summary.
- P50 mega synthesis and roadmap.
- Codex prompt sequence P50–P107.
- Assistant roadmap synthesis after P107.
- This archive package.

## Major Source Blocks

- Block 1 — Blockers Must Be Resolved Autonomously
- Block 3 — Eureka as Evidence-First Resolver
- Block 4 — Fast Learning, Slow Truth
- Block 5 — Public Search Must Not Fan Out Live
- Block 6 — Generated Through P107, Live Around P95
- Block 8 — Manual Observation Batch 0 Is Human Work
- Block 10 — Dry-Runs Are Not Authoritative Stores
- Block 13 — Public Alpha Should Be Minimal and Honest

## Likely Overlap With Other Chats

This chat likely overlaps with chats that generated earlier P50–P78 prompts, chats that executed individual prompts, deployment-specific chats, and repository-audit chats. Those other chats may contain actual command outputs, commits, and file details missing here.

## Likely Conflicts With Other Chats

Other chats may show that the live repository is ahead of or behind P95, or that P96–P107 have since landed. Other chats may also revise the next prompt numbering. Resolve conflicts by repository state and explicit user decisions, not by this archive alone.

## What To Preserve In A Master Book

Preserve the doctrine, the clean-room prompt method, the phase sequence, the public search boundary, the connector approval model, the dry-run-before-runtime model, and the human baseline requirement. Preserve the narrative of moving from prompt generation toward public alpha.

## What Not To Assume

Do not assume generated prompts are implemented. Do not assume hosted deployment exists. Do not assume manual baselines are complete. Do not assume the user accepted every assistant recommendation. Do not assume connector approval implies live runtime.

## Recommended Merge Handling

Merge this chat as a planning/governance chapter, not as an implementation log. Use repository audits to confirm completed milestones. When aggregating, map this chat’s prompt sequence against actual commit history and mark mismatches explicitly.
