# Human Archive Report — Eureka Workbench and Internet Archive Pilot

_Date anchor used for this report: 2026-05-31 Australia/Melbourne, per user instruction._

## 1. Orientation

This chat was mainly about turning Eureka from a large, evolving search-engine architecture into a runnable, testable local artefact-resolution system. The conversation began from a broad planning problem: the project had accumulated many tracks, bundles, source families, local-runtime pieces, and safety policies, and the user wanted to know where the work actually stood, what was real, what was only planning, and how to make the system usable on a local machine. Over the course of the chat, the discussion narrowed into a concrete engineering direction: the Local Appliance and Workbench should become the proving ground for every future capability, and the Internet Archive metadata connector should become the first complete source-family vertical slice.

The user’s main pressure was practical. They did not want more disconnected plans, scaffolds, or impressive-looking governance files that failed to produce a usable product loop. They wanted to be able to clone the repository, run a local HTML page, search the local index, start a Hunt for unresolved queries, run bounded source work, inspect evidence, review candidates, rebuild the local index, and eventually use that same workbench as the internal superset of the final Eureka websites, APIs, native apps, and possible marketplace-style clients. The user repeatedly corrected the direction away from one-off prompts or “half-assed” task bundles and toward end-to-end proof: local runtime behavior, persistent state, tests, audit evidence, clear boundaries, and a workflow that can be exercised repeatedly.

A major outcome of the chat was the decision to make the Workbench more than an admin dashboard. It should be “Eureka Mission Control”: an overpowered internal/operator version of the final product, built on the same backend contracts, routes, view models, source cache, evidence ledger, candidate index, review queue, and reviewed index that future public and native clients will use. The public website should later be a restricted projection of the same kernel, not a separate rewrite. This decision matters because it defines how future frontend, backend, source, search, evaluation, and native work should converge rather than branch apart.

Another major outcome was the staged Internet Archive metadata pilot. Across the visible task-status reports in this chat, the project moved through a sequence labelled IA-00 through IA-07, followed by IA-PILOT-CLOSEOUT-01. According to the pasted task outputs, the IA pilot reached a local end-to-end metadata vertical slice on `dev`: policy approval; fixture replay; a bounded live metadata probe; TLS trust diagnosis and repair; source-cache records; evidence candidates; provisional candidates; review queue and promotion dry-run; reviewed local index rebuild; search, object, and absence proof; and final closeout. The task outputs repeatedly emphasized that all writes were bounded to temporary explicit instances, no raw live response was committed, no master index was mutated, no downloads or uploads were performed, no extraction ran, no model/provider calls occurred, and no production/public launch readiness was claimed.

The future relevance of this chat is high. It captures a transition from strategic planning to a working local source-backed pipeline. It also captures the boundaries that must not be lost: live metadata observations are not truth, candidates are not reviewed records, review is required before local promotion, reviewed local index is not master index, and full Archive.org integration is not the same as a metadata pilot. It records that the next important product layer is not simply “more connectors,” but Workbench Foundation plus a Search Interaction Contract: full-sentence query input, compiled intent, live resolution runs, result lanes, pause/resume/deepen controls, user feedback, source/evidence/candidate/review state, and reusable resolution memory.

A future reader should understand the rest of this report as a record of convergence. The conversation moved through broad roadmap debates, local-machine readiness, repository structure, Internet Archive source integration, and Workbench-as-final-system design. The chat contains many long prompts and status reports, but the substance is a consistent architecture: one generic artefact-resolution kernel, many domain/source packs, one powerful operator Workbench, and safer public/native projections later. The most important lesson is that Eureka’s product value is not merely searching the web. It is turning difficult searches into governed investigations that produce evidence, reviewable candidates, source memory, and eventually reliable local or public results.

## 2. The Story of the Conversation

The conversation opened from a state of uncertainty about the overall Eureka plan. The user asked where the project was, what the plan ahead should be, what had been built, and when it would be possible to spin up a machine and test on the local network. At that stage, the project was described in terms of many tracks: representation/view models, observations, source/evidence/candidate networks, snapshot/relay, native clients, hosting, extraction, ranking, source expansion, packs, actions, semantic/AI assistance, and wider clients. The assistant suggested adding a Track 0 for queue/state/control hardening and then reorganising the plan into a more explicit sequence. This was an early sign of the conversation’s central concern: the user wanted durable control over the project state so future work would not drift.

The next shift was toward the Local Appliance. The user wanted the plan “forked” so Eureka could be hosted on any local machine, searched from a real HTML page, run agents and tests, and ground future work in a real local clone rather than more contracts. The assistant proposed inserting a Local Appliance / Local Network Workbench track before extraction and further source expansion. This became a key decision: future features should be proven through a local hosted system. The Local track was designed to create an explicit instance layout, a localhost service, an HTML workbench, a WorkUnit queue, source probe runner, review/rebuild flow, deterministic agent runner, auto-test harness, LAN safety gate, LAN smoke test, clean-machine bootstrap proof, and closeout.

The user then generated and executed a series of prompts outside the chat, returning status blocks. LOCAL-00 inserted the Local Appliance track. LOCAL-01 added explicit instance bootstrap and validation. Additional tasks progressed through local service, workbench, WorkUnits, review/rebuild, worker runner, auto-testing, LAN mode, clean-machine proof, and closeout. A later “final state” status claimed the R0 and LOCAL state were promoted to `main`, with hard blockers at zero and warnings explicitly classified. That status was later complicated by branch divergence reports, which became another recurring theme: generated repo-health claims could become stale, and branch reconciliation needed to be treated as part of product quality.

The HUNT track followed. The conversation treated HUNT as the active search/investigation spine: Search Hunt Sessions, pause/resume/steer, WorkUnits, SearchNeeds, exhaustion reports, background runners, deterministic replay, AI escalation gates, and closeout. The user repeatedly asked for “next” prompts and reported passes. HUNT eventually reached a promotion-review sequence, but a branch reconciliation problem emerged: `main` contained a newer AIDE/control-plane/source-slice baseline, while `dev` contained HUNT/search work using older AIDE state. The assistant recommended merging `origin/main` into `dev`, not `dev` into `main`, while preserving HUNT work and adopting the newer AIDE baseline. This branch reconciliation was an important operational lesson: the repo was complex enough that branch state itself had to be treated as a governed task.

After HUNT and Local Appliance work, the conversation turned toward making the system usable. The user asked how to search, hunt, administer, run locally, and test. The assistant summarised the mental model: Search equals local reviewed-index lookup; Hunt equals a workflow for hard or unresolved searches; Admin equals AIDE queue, repo-health, local instance status, operator tokens, and validators; Local run equals starting the localhost service; Testing equals fast checks plus promotion-grade validation when needed. The user then moved the `eureka-instance` directory outside the Git repo, preferring instance state beside the source tree rather than mixed into it. This led to a discussion of best-practice workspace layout, culminating in a preference for `../instances/default` as the canonical local instance path and explicit legacy support for `../eureka-instance`.

The next major phase was PLAY. After fixing instance-layout issues and broad-lane failures, the user proceeded through PLAY-00, PLAY-01, and PLAY-02. PLAY created a local demo corpus, a safe operator play session, and a demo query/absence/Hunt smoke pack. The purpose was to make the local workbench visibly useful before connecting real sources. The demo material included known hits, known absences, media SearchNeeds, extraction/source SearchNeeds, hard source-routing queries, compatibility queries, and blocked source/extraction/AI demos. This made future IA and SYN work testable against a real local loop rather than an empty index.

Then the Internet Archive metadata pilot became the first real source-family vertical slice. The user progressed through IA-00 to IA-07 and closeout. IA-00 approved a metadata-only local pilot policy with runtime disabled. IA-01 added deterministic fixture replay. IA-02 added and attempted a bounded live metadata probe, but initially failed due to a local Python TLS trust issue. Two TLS follow-up tasks diagnosed and repaired the shell’s TLS trust using an existing local Python CA bundle via `SSL_CERT_FILE`, without disabling TLS verification. The live probe then succeeded with two HTTPS requests, committing only redacted summary and normalized preview material. IA-03 added source-cache writes to a temporary explicit instance; IA-04 converted source-cache records into evidence candidates; IA-05 converted evidence into provisional candidate records; IA-06 added review queue and promotion dry-run; IA-07 rebuilt a reviewed local index and passed search, object, and absence proofs. IA-PILOT-CLOSEOUT-01 closed the pilot, with warnings about full discovery failures outside the IA lane but zero IA hard blockers and no production/public launch claims.

Near the end, the user asked whether Eureka could now run the engine and browse Archive.org “in full” live. The answer was no. The IA metadata pilot was complete, but a full live Archive.org browser/crawler/deep indexer was not built. The distinction was crucial: Eureka could prove the metadata vertical slice, but it could not yet take a local HTML query, automatically run an IA Hunt, stream candidates into the page, search all IA metadata, inspect all item files, fetch archives, unpack packages, index subdirectories, and deep-extract contents. That would require IA-HUNT integration, Workbench result lanes, polling or streaming events, operator-instance apply gates, scaled metadata query planning, item/file manifest expansion, source frontier queues, and eventually F0 extraction.

The final conceptual turn was toward the Workbench and repo structure. The user argued that the Workbench should be a proving ground for the final system, not merely a developer tool. The assistant agreed and recommended treating the Workbench as the internal superset of the final product: a Mission Control surface for search, Hunt, source cache, evidence, candidates, review, index, SYN, DOMAIN, SCOUT, extraction, snapshots, relay, and operations. The public website and native apps should later be restricted projections over the same kernel. The user then provided a repo-structure canon prompt and a filesystem tree, asking for the best repo structure to implement all these plans. The report recommended retaining the current major roots but imposing stricter ownership, adding `tools/`, `release/`, and `archive/` as explicit roots, separating runtime, surfaces, contracts, examples, tests, evals, and generated/local state, and adding layout validators before large moves.

The final state of the visible chat is therefore a project at the end of its first real external-source local pilot, with an emerging next phase: promote the IA pilot baseline, lock repo layout and Workbench placement policy, define the Search Interaction Contract, implement Workbench result lanes and events, bridge IA into HUNT, then begin SYN pressure-testing.

## 3. Main Themes

### The Workbench as the internal superset

A central theme was the transformation of the Workbench from a convenience dashboard into the internal superset of the final Eureka system. The user explicitly wanted the Workbench to be overpowered and usable for all project work, so backend and frontend bugs would be discovered before deployment. The assistant framed this as “Eureka Mission Control”: the operator surface where every kernel feature is proven before it becomes public or native. This theme matters because it prevents a common failure mode: building a backend pipeline, a separate admin page, and then later rewriting a public product from scratch. The conclusion was that the Workbench should use the same packets, routes, source/evidence/review/index machinery, and view semantics as future public web, API, CLI, TUI, relay, snapshot, native, and mobile clients. The unresolved part is implementation: the idea was accepted conceptually, but specific `WORKBENCH-FOUNDATION-00`, `SEARCH-INTERACTION-00`, and result-lane tasks still remain future work.

### Search as a live investigation

Another major theme was that Eureka search should not be a one-shot lookup. The desired product behavior is: local reviewed-index results appear instantly, unresolved or weak searches become Hunts, bounded source jobs run, candidates and evidence appear progressively, users can pause/refine/deepen, review decisions can promote candidates, and future searches benefit from the work. This theme evolved from earlier HUNT planning and became sharper after the IA pilot. The chat concluded that Eureka needs a Search Interaction Contract defining full-sentence queries, compiled intent, ResolutionRun state, result lanes, partial results, controls, feedback events, coverage reports, absence reports, and discovery trails. Without that contract, the Workbench may have pages but not coherent interaction semantics. This remains one of the most important next tasks.

### The Internet Archive metadata pilot

The Internet Archive pilot became the concrete proof that Eureka could connect a real external source to the local evidence/review/index loop without compromising safety. The chat followed a staged sequence from policy to fixture replay, live probe, source cache, evidence, candidates, review, reviewed local index, and closeout. The pilot mattered because it moved Eureka beyond demo-only behavior while preserving boundaries: metadata only, no downloads, no uploads, no public fanout, no raw response committed, no master index mutation, and no production claims. The conclusion was that Tier 0 IA metadata pilot is effectively complete on `dev`. What remains unresolved is the larger IA connector: Workbench integration, IA-HUNT bridge, scaled metadata search, file manifest expansion, and later extraction/member discovery.

### Safety, boundaries, and non-claims

The user consistently valued not overclaiming. The assistant repeatedly distinguished local reviewed records from master-index truth, metadata observations from evidence, evidence candidates from accepted evidence, candidate records from reviewed results, and reviewed local index from production/public index. Rejected or deferred features included downloads, extraction, public fanout, broad crawling, model/provider calls, marketplace-style actions, and production hosting. This theme will matter in any future aggregation because it prevents misreading the chat as a launch plan. The project moved toward more capability, but its safety posture remained fail-closed.

### Repository structure as architecture governance

Near the end, repo structure became a first-class theme. The user provided a repo-structure canon prompt and a large tree. The assistant concluded that the existing top-level roots were broadly appropriate but internally messy. The repo needed stricter ownership rules, not cosmetic reshuffling. Important issues included duplicate contract authority, generated AIDE exports, retained audit evidence, runtime fixtures/tests, `site/dist`, native build outputs, `data/public_index` ambiguity, and the need to move heavy scripts into `tools/` while keeping `scripts/` as thin wrappers. The conclusion was to add layout contracts and validators first, then do incremental refactors.

### Domain expansion, SCOUT, SYN, and eventual product ecosystem

The chat repeatedly returned to the larger vision: Eureka as a general artefact-resolution engine. Software, drivers, frontier-resolution media, manuals, scans, package registries, source releases, and other domains should become domain packs over one kernel. SCOUT, inspired by Archillect, should become a relation graph and source-path learning layer, but not a popularity engine or crawler. SYN should become synthetic query/eval pressure, but not fake evidence. Native apps, relay, snapshots, public hosting, marketplace-style managers, and action systems remain later tracks. The chat concluded that these ideas are valid, but their order matters: canonicalise IA and Workbench first, then SYN, DOMAIN, SCOUT, F extraction, ranking, broader sources, and only much later hosting/native/marketplace.

## 4. What We Were Actually Trying To Achieve

The explicit user goal was to understand and advance Eureka’s practical implementation state. The user asked where the project stood, what was left to build, whether the local workbench could search and hunt, whether Archive.org could be browsed in full, what repo structure could support the plan, and how to make the Workbench powerful enough to serve as a proving ground for the final product. The user wanted actionable sequencing, not generic strategy.

A second explicit goal was to preserve end-to-end quality. The user repeatedly insisted that tasks should not be half-finished, that validators should pass or failures should be classified, that warnings and blockers should be handled, and that each series should leave the project more canonical. This led to tasks such as instance-layout fixups, AIDE eval green, HUNT warning-zero closeout, IA closeout, and repo-layout canon planning.

An inferred goal was to prevent the project from becoming a mass of generated governance artifacts without a real product loop. This was not merely an aesthetic concern. The user wanted a local machine, a real HTML page, a local clone, and a repeatable engine workflow so future development would be grounded and testable. The Local Appliance, PLAY, HUNT, and IA pilot all served that inferred goal.

Another inferred goal was to build toward a universal artefact-resolution engine. The user’s examples included old software, Windows compatibility, advanced-format media, Internet Archive footage, archive members, subdirectories, package files, and eventually marketplace-like manager apps. The chat treated these not as separate products but as future domain packs and source families over one kernel.

Goals changed over time. Early in the conversation, the next step seemed to be F0 extraction or H-source expansion. That was superseded by the Local Appliance, then by HUNT closeout, then by PLAY, then by IA metadata pilot. Later, after IA closeout, the next goal shifted again: not “more IA depth immediately,” but making the Workbench the internal superset and adding Search Interaction contracts so the IA pipeline could be experienced through the UI.

Remaining unresolved goals include production hosting, native clients, marketplace/app-store-style managers, full Archive.org deep search, file downloads, extraction, source-family expansion beyond IA, SCOUT relation discovery, SYN eval foundry, and public projections. These goals matter, but the chat repeatedly placed them behind the local Workbench and source/evidence/review/index loop.

## 5. Decisions and Commitments

### Make the Local Appliance the proving ground

The chat committed to inserting a Local Appliance / Local Network Workbench track before further extraction and source expansion. This was accepted by the user through repeated “proceed” and “next” task generation, followed by status reports showing LOCAL tasks completed. The rationale was that future F/G/H work should be tested through a real local hosted system, not just contracts and audit packs. Alternatives included continuing directly into F0 extraction or more source-family bundles; those were deprioritised. This decision depends on the assumption that local runtime proof is more valuable than breadth at this stage. It could be revisited only if the project deliberately changes to a static-only or backend-only scope, which the visible chat does not support.

### Use a sibling instance layout

The user moved the `eureka-instance` folder outside the repo and preferred not to mix code with instance state. The ensuing tasks standardised around `../instances/default`, while keeping `../eureka-instance` as a legacy sibling. This was accepted through INSTANCE-LAYOUT tasks and fixups. The consequence is that repo source and mutable local state are separated. This supports clean Git status, safe testing, and future multiple-instance workflows. It may need future migration tooling, but the principle is settled in this chat.

### Complete PLAY before deeper source work

The chat decided to add PLAY seed corpus, operator session, and smoke pack before relying on IA or SYN. This was accepted and executed through PLAY-00, PLAY-01, and PLAY-02. The reason was that the Workbench needed known hits, absences, demo Hunts, demo SearchNeeds, demo WorkUnits, and blocked-path examples so local play and tests were meaningful. The alternative was connecting Archive.org immediately against a sparse index. PLAY made the system legible.

### Build Internet Archive as the first real source pilot

The chat committed to an Internet Archive metadata-only local pilot, not full Archive.org integration. This decision was accepted and executed through IA-00 to IA-07 and closeout. It made sense because Archive.org metadata is a valuable source family and can be integrated metadata-first without downloads. It also provided a reusable pattern for future source families. The decision explicitly excluded broad crawling, downloads, write APIs, public fanout, and unreviewed truth. The consequence is that IA became the first complete source-backed vertical slice.

### Treat TLS trust failure as local-machine configuration, not a reason to weaken security

During IA-02, the approved live metadata probe failed due to `ssl_certificate_verify_failed` / `self_signed_certificate_in_chain`. The chat decided not to disable TLS verification, not to use unverified contexts, and not to add insecure fallbacks. Instead, diagnostics were added and the shell was repaired using an existing local Python CA bundle via `SSL_CERT_FILE`. The probe then succeeded. This decision is important because it preserved security posture while still enabling the live probe.

### Close IA pilot before moving to SYN

After IA-07, the chat proceeded to IA-PILOT-CLOSEOUT-01 rather than jumping straight to SYN. The closeout validated all IA stages, produced matrices and docs, and handed off to SYN. This was accepted by the user via the PASS_WITH_WARNINGS closeout status. The consequence is that SYN can now pressure-test a real IA-backed local flow rather than a partial source pipeline.

### Make the Workbench the internal superset of the final system

The user explicitly stated that the Workbench should not be “just any old developer tool” but should be built as if it were the final system’s overpowered admin/developer version. The assistant agreed, framing it as the internal superset from which public web, API, CLI/TUI, relay, snapshot, native, and mobile clients can be projected. This is a conceptual decision, not yet fully implemented. It supersedes any plan to treat the Workbench as disposable admin UI.

### Add a Search Interaction Contract before deep UI/source expansion

Near the end, the chat identified a missing explicit contract for rich query interaction: full-sentence user queries, compiled intent, resolution runs, result lanes, controls, feedback events, and coverage reports. This was accepted in the user’s synthesis and became part of the recommended next sequence. It is not yet executed. It should guide future Workbench implementation.

### Stabilise repo structure by ownership and validators, not a giant move

The repo-structure discussion concluded that Eureka’s top-level roots are broadly appropriate but need governance. The recommended next task was `REPO-LAYOUT-CANON-00` to lock ownership roots, naming policy, generated-state policy, and Workbench placement before broad feature work. This was a recommendation, not yet reported as executed. It intentionally avoids a giant file move until validators exist.

## 6. Rejected, Superseded, or Deprioritised Ideas

### Continuing directly to F0 extraction

F0 extraction was repeatedly considered as a next phase, but it was superseded by Local Appliance work and later by HUNT, PLAY, IA, Workbench Foundation, and Search Interaction. The reason was that extraction without a local workbench, review flow, source pipeline, and eval pressure would risk becoming isolated tooling. F0 remains important, especially for archive/package/member discovery, but it is deferred until the Workbench and source/eval loops are stronger.

### Treating the IA pilot as full Archive.org integration

This was explicitly rejected. The IA pilot proves metadata-only search/read, source cache, evidence, candidates, review, reviewed local index, and search/object/absence proof. It does not prove full Archive.org browsing, collection crawling, downloads, file fetches, Wayback replay, archive extraction, or public fanout. This rejection is temporary in the sense that deeper IA layers are planned, but final only with respect to current claims: the current system must not be described as full IA integration.

### Letting the HTML page search all of Archive.org deeply while the user waits

The user wanted live progressive results from Archive.org, including metadata, files, archives, subdirectories, and packaged files. The assistant rejected the synchronous “search all of IA deeply” interpretation and reframed it as progressive, budgeted source discovery: local index first, cache next, bounded metadata jobs, item metadata, file manifest, candidates, review, and deeper extraction only through WorkUnits. The rejected synchronous approach would be slow, unsafe, rate-limit-prone, and architecturally brittle.

### Enabling downloads, extraction, or marketplace actions early

Downloads, extraction, install/execute actions, mirroring, emulator/VM handoff, and marketplace-style apps were repeatedly deferred. The reason was safety, rights, malware risk, resource limits, archive bombs, path traversal, and lack of review/action policy. These ideas may return under F0 and J tracks, but the chat made clear they should not be enabled during the IA metadata or Workbench foundation phase.

### Using AI as truth or first-line source research

AI assistance was discussed as a future candidate-only worker or relation-expansion helper, not a truth source. The assistant repeatedly stated that AI output should produce candidates, source leads, alias hypotheses, WorkUnits, and drafts, not accepted records, rights clearance, safety claims, or master-index mutations. This was not a rejection of AI entirely, but it deprioritised AI until deterministic HUNT, SCOUT, source policy, and review gates exist.

### Building SCOUT as a popularity engine

The Archillect-style idea was accepted only after rejecting the engagement/popularity model. The useful transplant is relation walking and feedback learning, not maximising clicks or aesthetics. SCOUT should optimise resolution value, evidence quality, provenance strength, source reliability, and hard-find usefulness. It should emit candidates, trails, trust observations, and WorkUnits, not public truth.

### Rewriting the repo into a pretty new tree immediately

The repo-structure canon warned against cosmetic restructuring. The assistant recommended preserving the current major roots and adding ownership contracts and validators before moving large trees. A giant move is deprioritised because it risks breaking references and masking authority problems. The current recommendation is phased: inventory, policies, validators, then targeted cleanup.

### Treating the public app, admin app, and native clients as separate products

This was rejected in favour of one kernel and many projections. The Workbench is the internal superset; public web and native clients are restricted surfaces over shared packets. This avoids duplicated semantics and future rewrites.

## 7. Rationale, Tradeoffs, and Design Logic

The dominant tradeoff in this chat was breadth versus proof. The user’s long-term ambitions are broad: all Archive.org layers, web/forum fallthrough, SCOUT discovery, synthetic evals, extraction, ranking, domain packs, native apps, mobile apps, and marketplace managers. But the chosen path consistently prioritised one complete local loop over many shallow integrations. That is why the IA metadata pilot was built deeply through source cache, evidence, candidate, review, and reviewed local index before adding Wayback, GitHub, packages, or other sources.

Another tradeoff was local power versus public safety. The Workbench is intended to become overpowered, but only for the local/operator context. Public web should later be a constrained projection. This design prevents unsafe operations from leaking into public mode. It also lets the project discover product and backend bugs early without pretending the system is production-ready.

A third tradeoff was human readability versus machine governance. The user wanted careful archive reports and human-readable briefs, but the project itself relies heavily on contracts, policies, validators, and audit packs. The conversation settled into a hybrid model: contracts are machine-readable authority; docs explain; audits preserve evidence; Workbench makes behavior visible; validators prevent drift. This prevents prose-only architecture from becoming stale while still preserving rationale for future readers.

The IA pilot’s design logic was conservative but powerful. Each stage added one authority layer and kept the next authority closed. Source cache did not write evidence. Evidence did not write candidates. Candidates did not write review. Review produced promotion previews only. Reviewed local index wrote only to temp explicit instances. That staged design makes future bugs easier to localise and prevents source metadata from becoming truth too early.

The TLS episode illustrated a security tradeoff. The user wanted a live probe, but TLS failed. The project could have bypassed verification, but that would have weakened the connector’s safety model. Instead, the chat held the line: diagnose environment, preserve verification, repair shell trust, rerun within policy. This approach took longer but preserved the integrity of the source pipeline.

The repo-structure discussion applied a similar tradeoff. A clean tree is desirable, but moving files without authority contracts would create new drift. The better path is to define roots, naming, generated-state policy, and validators before moving major subsystems. That slows visible reorganisation but prevents repeated root-level redesign.

The user seemed to care most about end-to-end usefulness, durable state, and not wasting work. The visible rationale behind nearly every recommendation is to make current work reusable: Workbench as future public projection, IA pilot as source-family pattern, SYN as pressure over real behavior, DOMAIN packs as generic semantics, SCOUT as relation discovery, F0 as gated extraction, and native/mobile clients as later consumers of stable contracts. If future work misunderstands this context, it may optimise for breadth, generate more task scaffolding, or prematurely build public/native surfaces before the kernel and Workbench are proven.

## 8. Current State at the End of This Chat

At the end of the visible chat, the most recent user-provided status is `IA-PILOT-CLOSEOUT-01` with `PASS_WITH_WARNINGS`. It states that the IA metadata pilot was closed through IA-07 reviewed local index proof, closeout matrices, validator, docs, tests, audit pack, and SYN handoff were added, the working tree was clean, `dev` was ahead of `origin/dev` by one commit, full IA metadata vertical slice was complete, full Archive.org integration was not claimed, hard blockers were zero, warnings were zero, and full unittest discovery still had broad-lane failures outside the IA lane. It also states no raw response was committed, no operator instance was mutated, no committed public index or master index was mutated, no downloads/uploads occurred, no extraction or model/provider calls happened, no deployment occurred, and no production/public launch readiness was claimed.

The assistant later stated that public `main` still reflected a prototype posture and that `dev` was ahead of `main`, but those claims depended on available repo/context information and may require verification. The safe summary is: based on visible user status, the latest IA work is on `dev` and may not yet be promoted to `main`. Therefore `IA-TO-MAIN-PROMOTION-REVIEW` remains a likely next operational task.

Settled: Local Appliance, HUNT, PLAY, and IA metadata pilot are treated as complete enough on `dev` for planning next phases. Tentative: Workbench Foundation, Search Interaction, IA-HUNT bridge, SYN, DOMAIN, SCOUT, F0, and repo-layout canon are recommended next phases but not yet reported as executed. Blocked or not yet enabled: full Archive.org deep browsing, downloads, extraction, public fanout, production hosting, native app store/marketplace behavior, and public launch.

The current immediate decision point is whether to promote the IA pilot baseline to `main` before starting Workbench Foundation/SYN. The assistant recommended promotion review first, then Workbench Foundation and Search Interaction. The user has not yet reported executing promotion review in this visible chat.

## 9. Future Work and Next Steps

### 1. IA-to-main promotion review

This should verify that the IA pilot closeout on `dev` is clean, reconcile with `main`, classify remaining broad-lane full-discovery failures, confirm no production/public claims, and promote if safe. It matters because SYN and Workbench Foundation should ideally start from a canonical baseline. Dependencies include a clean working tree, pushed `dev`, passing IA validators, and explicit disposition of full-discovery broad-lane failures. The output should be a promotion review report and, if appropriate, a fast-forward or merge to `main`. Failure modes include promoting unclassified test failures, stale generated state, or dev-only assumptions.

### 2. Repo layout canon

The next structural task should lock ownership roots, naming rules, generated-state policy, and Workbench placement. The output should include repo layout contracts, root allowlist, naming policy, generated-state policy, current-state inventory, debt register, and validators. This matters because the Workbench and Search Interaction tracks will add new roots and packets; without governance, the tree may drift further. It should not move large trees yet.

### 3. Workbench Foundation

This task should define the Workbench as internal superset, route/view matrix, permission matrix, projection rules, page ownership map, and view-model inventory. It should set up routes such as `/search`, `/hunt`, `/need`, `/workunit`, `/source`, `/candidate`, `/evidence`, `/review`, `/index`, `/syn`, `/domain`, `/scout`, `/extraction`, `/ops`, `/snapshots`, and `/relay`. It matters because the Workbench will become the proving surface for final product behavior.

### 4. Search Interaction Contract

This is the most important missing product contract. It should define SearchRequestPacket, CompiledQueryPacket, ResolutionRunPacket, ResultLanePacket, PartialResultPacket, CandidateClusterPacket, ActionPosturePacket, SearchControlCommand, UserFeedbackEvent, SearchPlanPatch, AbsencePacket, CoverageReportPacket, and DiscoveryTrailPacket. It should also define the state machine for live searches and user controls. This should precede major SYN or IA-HUNT UI work so those systems test correct interaction semantics.

### 5. Workbench result lanes and events

The Workbench should show reviewed local results, candidates, source-cache hits, IA metadata candidates, review queue items, known absences, blocked actions, and running WorkUnits. Polling endpoints should come before WebSockets or SSE if simpler. This matters because the IA pilot is currently script/proof-heavy; result lanes make it user-visible.

### 6. IA-HUNT bridge

The IA vertical slice must be wired into the HUNT system: query miss to IA metadata WorkUnit, pipeline runner, progress/status reports, candidate preview cards, review queue handoff, and reviewed-index rebuild from UI. This will produce the milestone where typing a query in the Workbench starts an IA-backed Hunt and progressively improves local search.

### 7. SYN Foundry

SYN should generate and validate common, hard, compatibility, compound-object, absence, adversarial, latency, and public demo queries. It should seed SearchNeeds and WorkUnits but not fake evidence or verified records. It should pressure-test LOCAL/HUNT/PLAY/IA behavior.

### 8. DOMAIN and SCOUT

DOMAIN packs should define typed semantics for legacy software, drivers/support media, frontier-resolution media, manuals/scans, package/source releases, and other object families. SCOUT should then build fixture-only relation discovery, trails, source trust, and WorkUnit seeds. SCOUT should not start as a crawler.

### 9. F0 extraction/member discovery

Only after Workbench, SYN, DOMAIN, and SCOUT foundations should F0 implement sandboxed extraction, container detection, member enumeration, manifest/readme extraction, member evidence candidates, and review/index integration.

### 10. Later production, native, and marketplace layers

Hosted public search, native clients, mobile clients, relay/snapshots, app-store/marketplace managers, download/mirror/install actions, and preservation workflows remain later tracks. They require ops, safety, rights, review, security, and stable contracts.

## 10. Artifacts, Files, Prompts, and Outputs

The chat discussed or generated many prompts and status outputs. The most important are not individual file lists, but the stages they represent.

The Local Appliance prompt series created the local runtime/workbench foundation: queue reset, instance layout, localhost service, HTML workbench, WorkUnit queue, review/rebuild, deterministic workers, auto-test/search, LAN safety, clean-machine proof, closeout, and remediation. These should be preserved as evidence of the shift from planning to local runnable product.

The instance-layout prompt and fixups established the sibling instance model. The key artifact is the documented preference for `../instances/default` and explicit legacy support for `../eureka-instance`. This belongs in future operations docs and repo-layout material.

The PLAY prompts created local demo usability. PLAY-00 added the demo corpus. PLAY-01 added the operator play session. PLAY-02 added the demo query/absence/Hunt smoke pack. These should feed future SYN and Workbench tests.

The IA prompts are central. IA-00 through IA-07 and IA-PILOT-CLOSEOUT-01 form the first real source-family vertical slice. Their full prompts are too long to reproduce in this report, but each should be preserved in the chat archive. Their purpose was to move from source policy to fixture replay, live metadata, source cache, evidence, candidates, review, reviewed local index, and closeout.

The TLS prompts are worth preserving because they show the safety posture: TLS failure was treated as local trust-store configuration, not a reason to bypass verification. This contributes to future source connector policy.

The repo-structure canon handoff prompt uploaded by the user is central to the final repo-structure discussion. It provides general principles: small stable ownership roots, no generic wrapper folders, no duplicate authority, separation of generated/local state, no casual `src/` wrappers, and validators to prevent drift. The uploaded tree also matters because it showed actual current structure, including `.aide`, `contracts`, `control`, `runtime`, `surfaces`, `site`, `native`, `crates`, `examples`, `evals`, `tests`, and the sibling `eureka-instance`.

The final archive-report request itself is also an artifact: it defines how this chat should be preserved for a larger project book. It requires human-readable reporting first, structured appendices second, and explicit distinction between fact, inference, uncertainty, and project context.

## 11. Open Questions and Unresolved Issues

The largest unresolved issue is promotion: is the IA pilot on `dev` promoted to `main`, or still pending? The latest visible user status says `dev` was ahead of `origin/dev` by one commit after closeout; assistant-side statements suggested `dev` was ahead of `main`, but this should be verified before future work treats the IA pilot as canonical. Resolution requires running the promotion review or checking Git branch state.

The second major unresolved issue is how much full unittest discovery matters before proceeding. IA closeout reported full discovery failures outside the IA lane. They were called non-blocking broad-lane failures, but they still matter for eventual promotion or production claims. Resolution requires classifying those failures, ensuring they are not caused by IA/Workbench changes, and deciding whether they block main promotion.

Another open issue is the exact boundary between `runtime/source_observation`, `runtime/sources`, `runtime/connectors`, and future source-family structure. The repo-structure discussion recommended moving toward `runtime/sources/<source>` and stricter ownership, but this has not been executed. Resolution requires `REPO-LAYOUT-CANON-00` and subsequent targeted refactors.

The Workbench architecture is unresolved at implementation level. The chat decided conceptually that Workbench is the internal superset, but route/view matrices, permission models, packets, and UI pages still need tasks. Resolution requires `WORKBENCH-FOUNDATION-00` and `SEARCH-INTERACTION-00`.

Full Archive.org integration remains unresolved. The metadata pilot is complete, but scaled metadata search, IA-HUNT bridge, file manifest expansion, collection-scoped queries, paging, dedupe, source scorecards, selective fetch, quarantine, and extraction are not built. Resolution requires a phased IA-DEEP or IA-HUNT sequence.

Production hosting remains unresolved. The system is not a production search engine. It lacks public ops gates, rate limits, abuse controls, source fanout policies, observability, backup/rollback, incident response, and security/privacy/takedown review. Resolution requires E-track/public alpha work after local behavior is stronger.

Native and marketplace futures remain mostly conceptual. The chat discussed native clients and app-store-like manager apps, but deferred them. Resolution requires snapshot/relay contracts, action policies, pack trust, sandboxing, rights/malware handling, and stable APIs.

## 12. Risks and Failure Modes

A future assistant might over-compress this chat into “IA connector done.” That would be wrong. The IA metadata pilot is complete through reviewed local index proof, but full Archive.org integration is not done. Avoid this by preserving the tier distinction: metadata pilot, user-facing IA Hunt, scaled metadata search, file-list intelligence, extraction, production connector.

Another risk is treating temp-instance writes as operator-instance or production writes. IA-03 through IA-07 used temp explicit instances. Future work must add operator apply gates, backup/snapshot/rollback, audit logs, and explicit permission before mutating `../instances/default`.

A third risk is treating reviewed local records as master-index truth. The chat repeatedly distinguished reviewed local index from master index and public hosted index. Future work must preserve these labels.

A fourth risk is losing the safety posture. The chat repeatedly blocked downloads, uploads, extraction, AI provider calls, public fanout, production deployment, and rights/safety claims. Future prompts must not silently enable them.

A fifth risk is repeating rejected paths: continuing directly into F0, building SCOUT as crawler/popularity feed, trying to search all Archive.org synchronously, or building public/native/marketplace surfaces before Workbench and Search Interaction are ready.

A sixth risk is relying on stale branch-state claims. The chat contains pasted task outputs, assistant statements about branch state, and references to public `main`. Future work should verify current Git state directly rather than trusting archive prose.

A seventh risk is letting repo structure drift. The uploaded tree shows many generated/audit/prototype/test/fixture paths. Without layout contracts and validators, new Workbench and source work could worsen ambiguity.

## 13. Larger Project Contribution

This chat contributes a major chapter to the larger Eureka project. It records the transition from local architecture to a working external-source local pilot. It also articulates the product philosophy: Eureka is not just a search box, but an artefact-resolution engine where searches become investigations and sources become evidence through review.

The chat overlaps heavily with project work on Local Appliance, HUNT, IA metadata, Workbench design, repo layout, and future SYN/SCOUT/F tracks. It may conflict with older plans that placed F0 or broad H-source expansion earlier, or that treated the Workbench as a less central admin tool. The archive should preserve that the newer plan supersedes those older directions, at least in this chat’s context.

The chat should feed a future book or specification in several chapters: “Local-first Workbench,” “Search as Investigation,” “Evidence-first Source Connectors,” “Internet Archive Metadata Pilot,” “Workbench as Internal Superset,” “Repository Structure as Governance,” and “From Metadata to Deep Artefact Resolution.”

Some content should become formal requirements only after review: Search Interaction packets, Workbench routes, repo layout contracts, IA-HUNT bridge, SYN query taxonomy, DOMAIN packs, and SCOUT schemas. Other content should remain background rationale: estimates of readiness percentages, strategic comparisons, and speculative future marketplace/native paths.

Verification is needed before merging this report into a master project state: current Git branch state, whether `dev` was pushed/promoted, exact full-discovery failure classification, and the current tracked repo tree.

## 14. What To Remember

- The Workbench should be Eureka’s internal/operator superset, not a disposable admin page. Public web, API, CLI/TUI, relay, snapshot, and native clients should be projections of the same kernel.
- The IA metadata pilot, according to visible user task reports, completed on `dev` through reviewed local index proof and closeout. This is a major milestone, but not full Archive.org integration.
- The completed IA path is metadata-only and bounded: policy, fixtures, live probe, source cache, evidence candidates, provisional candidates, review queue, promotion preview, reviewed local index, search/object/absence proof.
- No raw live IA response was committed; no downloads/uploads, extraction, model/provider calls, public fanout, master index mutation, deployment, or production/public launch claim occurred.
- The next product need is an interactive Workbench: Search Interaction Contract, result lanes, live resolution events, IA-HUNT bridge, and operator review/rebuild flow.
- SYN should pressure-test real Local/HUNT/PLAY/IA behavior and must not generate fake evidence or fake verified records.
- DOMAIN packs and SCOUT are important but should follow Workbench and SYN foundations. SCOUT should be relation discovery, not popularity/crawling.
- F0 extraction/member discovery remains later because downloads/extraction require safety, rights, malware, sandbox, and resource controls.
- Repo structure should be governed by ownership roots and validators, not a giant cosmetic move. The current roots are mostly right; internal duplicate authority and generated-state leakage need cleanup.
- The immediate next likely tasks are IA-to-main promotion review, repo layout canon, Workbench Foundation, Search Interaction, Workbench result lanes/events, and IA-HUNT bridge.

## 15. Final Plain-English Summary

This chat documented a decisive stage in the Eureka Archive System project. The user wanted to know where the project actually stood, how to stop the plan from drifting, how to run and test the system locally, whether Internet Archive integration could be used live, and how to structure the repo and Workbench so future development would not be wasted. The conversation moved from broad planning to concrete evidence of progress: Local Appliance, HUNT, PLAY, and a full Internet Archive metadata pilot through reviewed local index proof.

The core idea that emerged is that Eureka should be built around a single artefact-resolution kernel. Search should not be a one-shot lookup. A query should become a live, controllable investigation: local reviewed results first, source cache and candidates next, Hunts and WorkUnits for unresolved needs, evidence candidates, review, promotion, and reviewed local index updates. This model is what makes Eureka different from a conventional search engine. It turns absence and ambiguity into reusable work.

The Workbench became central. The user argued that it should not be just a developer tool. The assistant agreed and reframed it as Eureka Mission Control: the internal superset of the final system. The Workbench should exercise the same backend contracts, view packets, search results, source cache, evidence ledger, candidate index, review queue, reviewed index, source policies, WorkUnits, evaluation tools, domain packs, SCOUT trails, extraction tasks, snapshots, relay readiness, and operations state that future public and native projections will use. This matters because it prevents the public product from becoming a later rewrite. If the Workbench is the proving ground, bugs in backend and frontend flows will be found while building the real system.

The Internet Archive metadata pilot was the chat’s biggest concrete accomplishment. The user pasted status reports showing IA-00 through IA-07 and closeout. The pilot began with policy approval and fixture replay, moved through a bounded live metadata probe, handled a TLS trust issue without disabling verification, wrote source-cache records, generated evidence candidates, created provisional candidate records, sent them through review and promotion dry-run, rebuilt a reviewed local index in a temporary explicit instance, and proved search, object, and absence packets. This is not full Archive.org browsing, but it is the first real external-source vertical slice. It proves the pattern that future source families should follow: policy, fixture, bounded live probe, source cache, evidence, candidates, review, local index, and closeout.

The chat was careful not to overclaim. Full Archive.org integration is not done. The system cannot yet open a local HTML page, search all of Archive.org deeply, stream all item/file/archive/member results, crawl collections, download files, unpack archives, or index subdirectories and packaged contents. Those remain future layers. The current state supports metadata-only proof and local reviewed-index projection. Deeper IA search will require IA-HUNT bridge, result lanes, event/polling APIs, item metadata expansion, file manifest expansion, source frontiers, rate/quota ledgers, dedupe, source scorecards, and later F0 extraction with quarantine and sandbox policies.

The conversation also settled important sequencing. Do not jump to broad source expansion, extraction, public hosting, native clients, or marketplace apps yet. The best next path is to promote or review the IA pilot baseline, lock repo layout and Workbench placement, define the Search Interaction Contract, implement Workbench result lanes and events, bridge IA into HUNT, then start SYN. SYN should pressure-test the real Local/HUNT/PLAY/IA flow. DOMAIN packs should then define object-family semantics. SCOUT should add relation trails and source trust, but only as review-gated candidate discovery. F0 extraction should follow when the system can safely handle files, archives, packages, and members.

The repo structure discussion concluded that the current top-level roots are broadly appropriate but internally need stricter governance. The project should keep roots such as `.aide`, `control`, `contracts`, `runtime`, `surfaces`, `site`, `snapshots`, `native`, `crates`, `examples`, `evals`, `docs`, `tests`, and `external`, while adding or clarifying `tools`, `release`, and `archive`. The key is not a big move but ownership contracts and validators. Generated/local state, AIDE exports, audit packs, runtime fixtures/tests, `site/dist`, native build outputs, `tmp`, and ambiguous `data/public_index` need classification. Scripts should be thin wrappers; heavy validators and migration tools should move to `tools`. Contracts should hold machine law, examples should hold canonical payloads, tests should hold fixtures, and control/audits should hold retained evidence.

The most important unresolved operational question is whether the IA pilot on `dev` has been promoted to `main`. The chat suggests it remained on `dev` at the end, with `dev` ahead of origin after closeout. A future assistant should verify branch state before proceeding. Another unresolved issue is full unittest discovery: IA closeout reported broad-lane failures outside the IA lane. These were classified as non-blocking for IA closeout, but they matter for promotion and production confidence.

The best next action is not to build another connector. It is to canonicalise the IA pilot baseline if needed, then build the Workbench Foundation and Search Interaction Contract. The future Workbench should let a user type a rich query, see local results immediately, watch IA candidates arrive, inspect evidence and source trails, review or reject candidates, rebuild the reviewed local index, and rerun the query to see improved results. That will be the point where Eureka becomes a real local active-search engine rather than a collection of backend proofs.

# Reader Status

- Chat title: Eureka Workbench and Internet Archive Pilot
- Report type: human-readable archive report
- Main value of this chat: Captures the transition from local architecture and planning into a working Local/HUNT/PLAY/IA metadata vertical slice, plus the decision to make the Workbench the internal superset of the final system.
- Most important decision: The Workbench should be the canonical proving ground and internal superset, with public/native surfaces as restricted projections over the same kernel.
- Most important unresolved issue: Whether the IA pilot baseline on `dev` has been promoted to `main`, and how broad-lane full-discovery failures affect promotion.
- Most important next action: Run IA-to-main promotion review or verify canonical branch state, then begin Workbench Foundation and Search Interaction Contract work.
- Safe for aggregation: with caveats
- Main caveats: Several repo-state claims come from pasted task outputs rather than independently verified Git state; full Archive.org integration is not complete; production/public launch readiness is explicitly not claimed.
