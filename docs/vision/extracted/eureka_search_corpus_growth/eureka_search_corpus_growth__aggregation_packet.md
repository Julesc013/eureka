# Aggregation Packet — Eureka Search Engine: Corpus Growth, Public UX, and Resilient Search Planning

## One-Paragraph Summary

This chat records the Eureka project’s shift from public-alpha launch preparation to governed reviewed-corpus growth and resilient search design. The user rejected premature launch because the public surface did not yet produce enough useful reviewed results. The project then built active discovery, candidate indexing, SCOUT relations, review batching, seed batches across four domains, live metadata pilots, local apply proofs, snapshot refreshes, public search UX, and repeated public-alpha reassessments. The final completed state is `SNAPSHOT-REFRESH-06`, with limited reviewed projections raised to 12 and candidate count after apply at 60. Public launch remains deferred; the next proposed task is `PUBLIC-ALPHA-REASSESS-06`, followed by indexless live fallback and search usefulness evaluation.

## Main Themes

- Governed temporal object resolution rather than generic archive search.
- Candidate richness versus reviewed truth.
- Public launch deferral despite route and UX progress.
- Review/apply/snapshot/reassess as the core corpus-growth machine.
- Full-discovery externalization to avoid AI token waste.
- No-JS evidence-first public UX.
- Resilience through future indexless live metadata fallback.

## Major Decisions

- Defer public launch.
- Make reviewed-corpus growth the main milestone.
- Keep live metadata candidate/review-bound.
- Keep downloads/extraction/OCR/model/public mutation disabled.
- Run long full discovery outside AI.
- Treat public UX MVP as necessary but not sufficient.
- Plan indexless fallback as a resilience track.

## Major Open Questions

- How to implement indexless live fallback safely.
- How to measure search usefulness against hard queries.
- What suffices for reviewed artifact records.
- When to run external full discovery and promote dev to main.
- When reviewed corpus is sufficient for public alpha.

## Major Artifacts

- Test-token discipline harness/policy.
- Public alpha defer decision.
- Query planner, candidate index, SCOUT, review batch.
- Seed batches: frontier media, legacy software, manuals/scans, driver/support.
- Live metadata pilot and local apply.
- Public search UX model and MVP.
- Snapshot refresh series through v6.
- Public alpha reassessment series through proposed v6.

## Major Source Blocks

- Quality, tokens, and time.
- Stop launching from an empty shell.
- Eureka as temporal object-resolution.
- Reviewed-corpus growth as the machine.
- Candidates are not truth.
- Test discipline.
- Public UX as search-first evidence surface.
- Indexless fallback remains missing.
- Launch gate remains strict.
- Latest completed state.

## Likely Overlap With Other Chats

Likely overlaps with repo-structure chats, Workbench architecture, IA metadata pilot, public alpha launch planning, UX design discussions, and test-harness conversations.

## Likely Conflicts With Other Chats

Possible conflicts if another chat suggests public alpha is launch-ready, public live fanout is enabled, or candidate counts imply reviewed truth. This chat says those are not true at its end.

## What To Preserve In A Master Book

Preserve the product identity, the launch deferral rationale, the reviewed-corpus loop, the test-discipline correction, the public UX design principles, and the resilience/indexless fallback plan.

## What Not To Assume

Do not assume repository statuses were independently verified. Do not assume proposed tasks were completed. Do not assume public launch, public live source search, downloads, OCR, extraction, or reviewed artifact records exist.

## Recommended Merge Handling

Merge this chat as a strategic milestone chapter: “From Public Alpha Shell to Reviewed-Corpus Engine.” Use task details as supporting chronology, not as the main narrative. Cross-check with repository state before formalizing exact commit history.
