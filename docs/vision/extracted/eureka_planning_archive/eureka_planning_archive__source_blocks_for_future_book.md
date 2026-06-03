# Source Blocks for Future Book — Eureka Planning, AIDE Control, Local Appliance, and Search Hunt Workbench

## Block 1 — Eureka is not just a search engine

Type:
- explanation / decision

Source status:
- FACT, because this theme is explicitly stated and repeated in the visible chat.

Text:
Eureka was framed as “not just a search engine,” but a local-first, evidence-backed, cross-era digital artefact resolver and service layer. The public website may feel like search, but the backend should behave like a resumable investigation engine.

Why this block matters:
This is the central identity of the project. It can be used in a future book chapter that introduces why Eureka exists and why normal search/product metaphors are insufficient.

Suggested future chapter/theme:
“From Search Engine to Evidence Resolver”

## Block 2 — The governing law of autonomy and truth

Type:
- decision / rationale

Source status:
- FACT, visible as repeated wording accepted across the conversation.

Text:
“Autonomy may discover. Candidates may propose. Evidence may support. Review may promote. Only reviewed evidence-backed records become public truth.”

Why this block matters:
This sentence captures the entire safety and governance model. It should be preserved nearly verbatim.

Suggested future chapter/theme:
“Fast Learning, Slow Truth”

## Block 3 — AIDE is control metadata, not product truth

Type:
- rationale / risk

Source status:
- FACT for the stated distinction; INFERENCE for its broader governance implications.

Text:
AIDE Lite was treated as a repo-local control plane for compact task packets, review packets, validation, and queue continuity. It was not treated as Eureka product truth. Product truth lives in contracts, runtime, accepted architecture docs, audits, and reviewed evidence.

Why this block matters:
This distinction prevents future agents from confusing generated AIDE state with the actual product. It also explains why stale repo-health files must not override branch comparison.

Suggested future chapter/theme:
“Control Planes and Product Truth”

## Block 4 — One truth, many representations

Type:
- decision

Source status:
- FACT, explicitly discussed in website/domain/capability planning.

Text:
The project should not split into separate old, modern, mobile, API, or retro products. It should use one canonical route space and object/evidence/action model, rendered through many negotiated representations.

Why this block matters:
This explains the architecture behind old-browser support, text output, API, snapshots, relay, and native clients.

Suggested future chapter/theme:
“Cross-Era Interfaces Without Forked Truth”

## Block 5 — Native directories by API family, not era

Type:
- decision

Source status:
- FACT.

Text:
Native client directories should use short, stable API/toolchain names such as `carbon`, `appkit`, `swiftui`, `win16`, `win32`, `winforms`, and `winui`. Do not encode “legacy,” “modern,” “classic,” or “old” in paths.

Why this block matters:
This is a concise design principle for long-lived monorepo organization.

Suggested future chapter/theme:
“Repository Names That Survive Time”

## Block 6 — Local appliance as product kernel

Type:
- decision / rationale

Source status:
- FACT for the plan as stated; INFERENCE for its architectural centrality.

Text:
The next phase after R0 should be a Local Appliance / Search Hunt Workbench, not immediate F0 extraction. The local product loop is clone, initialize local instance, start localhost server, open HTML workbench, search reviewed index, queue WorkUnits, review evidence, rebuild index, and run smoke/eval suites.

Why this block matters:
This marks a major transition from specification/governance to runnable local product proof.

Suggested future chapter/theme:
“The Local Appliance as Proof Surface”

## Block 7 — Search is a hunt, not only a lookup

Type:
- explanation / product design

Source status:
- FACT as a visible product-design conclusion.

Text:
A search should return known results immediately if they exist. If the system does not know the answer, it should start a governed hunt, create a SearchNeed and WorkUnits, run allowed probes, produce candidates and evidence, and preserve the investigation for review and future users.

Why this block matters:
This concept is one of Eureka’s strongest product differentiators.

Suggested future chapter/theme:
“Search as Resumable Investigation”

## Block 8 — Completion requires runtime proof

Type:
- decision / quality standard

Source status:
- FACT as a visible planning conclusion.

Text:
Contracts, policies, examples, and validators are not completion. A product task is not complete unless it proves behavior through runtime code, command execution, persistent state where applicable, tests, audit evidence, no forbidden side effects, and local workbench integration when applicable.

Why this block matters:
This prevents future work from accumulating attractive scaffolding without usable product behavior.

Suggested future chapter/theme:
“Proof, Not Paper”

## Block 9 — Branch comparison outranks stale generated state

Type:
- risk / decision

Source status:
- FACT based on visible GitHub connector results in the chat.

Text:
A generated repo-health file on `main` claimed `origin_main_equals_origin_dev: true`, but the live GitHub compare in the chat showed `main` and `dev` were diverged 13/13. The final recommendation was to trust live branch comparison over stale generated state.

Why this block matters:
This is a concrete operational lesson for AI-assisted development.

Suggested future chapter/theme:
“Generated State Can Lie”

## Block 10 — Current next action is branch/AIDE synchronization

Type:
- next step

Source status:
- FACT as the final assistant recommendation based on tool output; still pending execution.

Text:
The current next step is `DEV-MAIN-AIDE-SYNC-01`, followed by AIDE eval repair/classification, HUNT warning cleanup, HUNT perfect closeout, promotion review, and then SYN-00.

Why this block matters:
This is the final operational status of the chat.

Suggested future chapter/theme:
“Closeout Gates Before Expansion”

## Block 11 — Public hosting remains deferred

Type:
- decision / risk

Source status:
- FACT as repeated in visible planning and repo-health summaries.

Text:
No hosted public launch, source probes, extraction, model/provider calls, downloads, uploads, accounts, telemetry, production readiness claim, or public launch readiness claim should be assumed from the current state.

Why this block matters:
It protects the project from premature public/product claims.

Suggested future chapter/theme:
“Non-Claims as Product Safety”

## Block 12 — SYN before F0 after HUNT

Type:
- next step / rationale

Source status:
- FACT for dev task packet contents; INFERENCE for overall prioritization.

Text:
Dev’s task packet points to SYN-00 after HUNT-12. SYN should create query/eval pressure before extraction/source expansion resumes, while F0 can resume but is not recommended now.

Why this block matters:
This captures the latest product sequencing once branch synchronization is complete.

Suggested future chapter/theme:
“Testing the Search Nervous System Before Extraction”
