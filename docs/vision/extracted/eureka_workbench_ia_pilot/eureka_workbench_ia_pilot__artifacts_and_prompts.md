# Artifacts and Prompts — Eureka Workbench and Internet Archive Pilot

_Date anchor used for this report: 2026-05-31 Australia/Melbourne, per user instruction._

## Local Appliance prompts and outputs

Type: task prompts and pasted task status reports.

Purpose: Insert and complete a local workbench/appliance layer before further extraction or source expansion.

Contents: Tasks from LOCAL-00 through LOCAL-14, plus remediation and final closeout-style outputs. They covered instance layout, localhost service, HTML workbench, WorkUnit queue, review/rebuild UI, deterministic workers, auto-test/search, LAN safety, clean-machine proof, and closeout.

Status: Reported as completed in pasted statuses, with warnings handled in later remediation.

Preserve: yes. These establish the local-first proving-ground architecture.

Caveats: Exact repository state should be verified directly; visible chat contains pasted outputs, not a full Git log.

## Instance layout prompts

Type: task prompts and status reports.

Purpose: Standardize local instance state outside the repo.

Contents: Preflight docs review, instance-layout task, fixups for commit policy and clean-machine failures, path resolver, layout classifier, migration dry-run, validators.

Status: Reported as completed, with `../instances/default` preferred and `../eureka-instance` legacy sibling allowed.

Preserve: yes. This is important for all local runs.

## HUNT prompts and outputs

Type: task series and status reports.

Purpose: Build the Search Hunt spine: sessions, UI state, commands, exhaustion, SearchNeeds, WorkUnits, background runner, replay, AI escalation gate, closeout.

Status: Reported as completed/promoted in later status summaries.

Preserve: yes. HUNT is central to search-as-investigation.

Caveats: Some branch divergence and AIDE sync issues appeared around HUNT; future aggregation should verify current branch state.

## PLAY-00 / PLAY-01 / PLAY-02

Type: task prompts and status reports.

Purpose: Make the local Workbench playable and testable.

Contents: Demo corpus, known hit, known absence, media SearchNeed, extraction/source SearchNeed, hard source-routing query, compatibility query, blocked source/extraction/AI paths, operator play session, smoke pack.

Status: Reported as PASS.

Preserve: yes. PLAY should feed SYN and Workbench smoke tests.

## IA-00 through IA-07 prompts

Type: detailed task prompts and status reports.

Purpose: Build the first real external-source vertical slice using Internet Archive metadata.

Contents:
- IA-00: metadata-only policy gate.
- IA-01: fixture replay hardening.
- IA-02: bounded live metadata probe.
- TLS follow-ups: diagnostics and local trust repair.
- IA-03: source-cache write path.
- IA-04: evidence-ledger integration.
- IA-05: candidate-index integration.
- IA-06: review/promotion dry-run.
- IA-07: reviewed local index rebuild.

Status: Reported as PASS through IA-07, with IA-PILOT closeout PASS_WITH_WARNINGS.

Preserve: yes. This is the first complete source-family pattern.

Caveats: IA is metadata-only; not full Archive.org integration.

## IA-PILOT-CLOSEOUT-01

Type: task status report and closeout prompt.

Purpose: Summarize and validate IA-00 through IA-07 as a coherent vertical slice.

Contents: Capability matrix, validation matrix, boundary matrix, reuse matrix, warning disposition, blocker register, SYN handoff.

Status: User reported PASS_WITH_WARNINGS; hard blockers and warnings reported as zero for IA, but full discovery still had broad-lane failures.

Preserve: yes. It is the current best end-state summary for IA.

## TLS diagnostics and trust repair

Type: task prompts and status reports.

Purpose: Diagnose and fix Python TLS trust failure for IA live metadata probe.

Contents: Diagnostic scripts, TLS validator, decision not to disable verification, shell-level `SSL_CERT_FILE` fix using existing local Python CA bundle, successful live probe rerun.

Status: Reported as PASS.

Preserve: yes. This is a useful source-connector safety precedent.

## Archillect / SCOUT discussion

Type: conceptual design section.

Purpose: Adapt relation-walking and feedback-learning into a Scout / Curator Graph layer.

Contents: DiscoveryCandidate, CuratorRelation, DiscoveryTrail, SourceTrustRecord, HuntFeedbackEvent, relation paths, source trust, review-gated feedback.

Status: Conceptual; not implemented.

Preserve: yes. It should feed future SCOUT tracks.

## Advanced-format media / frontier-resolution media discussion

Type: product wedge discussion.

Purpose: Identify a second domain wedge beyond old-platform software.

Contents: New York 1993 D-Theater/HD footage, Hi-Vision/MUSE/D-VHS/large-format/city-symphony lineage, advanced-format everyday-life documentation.

Status: Proposed as future domain/search-need family; not implemented.

Preserve: yes. It contributes to the project book and DOMAIN pack planning.

Caveats: Some external provenance claims need current verification before publication.

## Repo Structure Canon Handoff Prompt

Type: uploaded file.

Purpose: Provide rules for deriving optimal repo structure from product goals, ownership roots, runtime model, data model, and future expansion needs.

Contents: Operating rules, root principles, no `src/source` doctrine, naming rules, contracts vs docs, Workbench/editor host rule, AIDE/generated-state rule, migration strategy, acceptance criteria.

Status: Used as source material in final repo-structure discussion.

Preserve: yes. It should guide `REPO-LAYOUT-CANON-00`.

## Uploaded directory tree

Type: uploaded file/tree snapshot.

Purpose: Show current filesystem layout around `D:\Projects\Eureka`, including `eureka` repo and sibling `eureka-instance`.

Contents: Large tree of `.aide`, `contracts`, `control`, `runtime`, `surfaces`, `site`, `snapshots`, `native`, `crates`, examples, evals, tests, and instance folders.

Status: Supporting material, not necessarily tracked-only.

Preserve: yes, but use carefully.

Caveats: Filesystem tree includes visible directories that may be untracked/generated/local. Future repo layout work must use `git ls-files` rather than raw tree alone.

## Archive request prompt

Type: user instruction.

Purpose: Generate this human-readable archive package.

Contents: Required seven files, main report structure, appendices, accuracy rules, distinction between FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT.

Status: Current task.

Preserve: yes. It defines the archival methodology.
