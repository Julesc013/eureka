# Human Archive Report — Eureka Planning, AIDE Control, Local Appliance, and Search Hunt Workbench

**Date anchor:** 2026-05-31 Australia/Melbourne  
**Scope note:** This report uses the visible contents of this chat. Where this chat included GitHub connector outputs, those outputs are treated as visible evidence from this chat. Where the report interprets the meaning of plans or statuses, it labels that as inference or uncertainty rather than fact. This report does not rely on hidden chain-of-thought.

## 1. Orientation

This chat was a long, iterative planning and control conversation for the `julesc013/eureka` project. At the highest level, the user was trying to turn a broad and ambitious archive/search idea into a durable engineering plan that could survive many future Codex/GPT-5.5 work sessions without drifting, overclaiming, or repeating earlier mistakes. The project at the center of the discussion, Eureka, was framed throughout as more than a search engine. It was repeatedly described as a local-first, evidence-backed, cross-era digital artefact resolver: a system intended to resolve vague user requests into actionable records about software, drivers, manuals, media, archived objects, old-platform-compatible artefacts, and evidence trails. The long-term vision includes search, known-need tracking, evidence review, local nodes, source packs, candidate records, snapshots, relays, native clients, and eventually a hosted public service. The user’s deeper goal was to make sure this vision could be implemented in the real repository without collapsing into either endless documentation or unsafe automation.

The conversation mattered because the project had reached a transition point. Earlier planning had produced many doctrines, tracks, queues, and prompt sequences: Track A for view models and representation, Track B for nodes and evidence/review, Track D for snapshot/relay, Track C for native clients, Track E for hosting, and later tracks for extraction, ranking, source expansion, federation, actions, AI, and wider clients. Later updates indicated that the repository had moved well beyond some of those earlier plans. AIDE Lite had been imported into Eureka as a repo-local control layer. Track A and Track B were reported as complete enough. Then dev was reported to have advanced through a local-MVP stack, then through LOCAL and HUNT work. The conversation therefore had to keep reconciling planning doctrine with repo state and branch state. A recurring theme was that stale generated task packets, stale repo-health reports, or old prompt queues must not be treated as product truth when live branch comparison and validation evidence disagree.

A central outcome of the chat was the elevation of “local appliance” and “Search Hunt Workbench” as the next product kernel. Instead of moving directly from runtime seams into deep extraction or broad source connector expansion, the plan pivoted toward building a runnable local product loop: clone the repo, initialize a local instance, start a localhost server, open an HTML workbench, search the reviewed index, create Search Hunt Sessions, queue WorkUnits, review evidence, rebuild the index, and run smoke/eval suites. The rationale was that future tracks should prove themselves through the local appliance, not only through contracts, validators, and audit packs. This changed the implementation philosophy from “contracts first” to “contracts plus runnable local proof.” The newer rule became: contracts, policies, examples, and validators are not completion by themselves; completion requires runtime behavior, persistent state where applicable, tests, negative tests, audit evidence, and local workbench proof where applicable.

Another important outcome was the refinement of “search” into “hunt.” Eureka’s future search behavior was not imagined as a single request-response lookup. A hard search should return what is known immediately, and if the result is weak or absent, create a governed Search Hunt Session. The session can create SearchNeeds, WorkUnits, source probes, candidate records, evidence records, exhaustion reports, and eventually reviewed public-index updates. The conversation repeatedly rejected uncontrolled crawling, scraping, live fanout, and AI-as-truth. It accepted the idea of bounded, policy-governed investigation: source policy, fixture replay, approved metadata-only probes, source cache, evidence candidates, review queue, reviewed-index dry run, search-quality delta, and postmortem.

The latest visible state in the chat was not merely a product-roadmap discussion. It became a branch-control and closeout discussion. The user quoted a plan that said main had the better AIDE/control-plane baseline while dev had HUNT product work, and that the next step should be to merge `main` into `dev`, resolve AIDE golden-task failures, clear or classify HUNT warnings, produce a perfect HUNT closeout, then run a promotion review before starting SYN-00. The assistant then used the GitHub connector inside the chat to check `main...dev` and found the branches were in fact diverged 13/13. It also inspected `main` and `dev` task packets and health reports. The assistant concluded that the product direction remained correct, but the operational next step was branch/AIDE reconciliation, not starting SYN or F0 immediately. This is one of the most important preservation points: generated repo-health files may become stale; live branch comparison and current validation evidence outrank stale generated claims.

A future reader should understand the rest of this report as the record of a project governance conversation, not only a technical design chat. The content captures a maturing development operating system: how Eureka should structure work, how AIDE should control context and prompts, how branches should be synchronized, how candidates and evidence should be separated from truth, how local product proof should precede hosted claims, and how long-term ambition should be staged safely. Some ideas in this chat are firm decisions accepted by the user, such as using AIDE Lite as a repo-local control layer, treating local appliance/HUNT as the product kernel, and reconciling main/dev before SYN. Other ideas are still proposals or planning doctrine, especially later Tracks F–L. The report preserves both categories while marking what remains tentative or unverified.

## 2. The Story of the Conversation

The conversation began with the user pasting earlier synthesized planning material about Eureka. The initial frame was that Eureka should not be “just a search engine,” but a local-first, evidence-backed, cross-era digital artefact resolver and service layer. In this early material, the public website was imagined as search-engine-like, but the backend was described as a resumable investigation engine. The purpose was to resolve vague requests into actionable artefact records: app versions, drivers, manuals, hidden files inside archives, compatibility notes, source records, evidence claims, action manifests, absence reports, and confidence judgments.

The user then clarified that the actual repo was on GitHub under `julesc013/eureka`. This shifted the conversation from abstract architecture to repo-grounded planning. The assistant responded by connecting the plan to the repo’s broad posture: Eureka was treated as a local-first temporal object resolver and not a production app store, downloader, native GUI app, LLM-first wrapper, or open-internet production service. The early discussion established that the project was contract-heavy but already had substantial Python reference-backend slices and public/static surfaces. The conversation then refined the website design: one canonical backend and route space, many negotiated representations, no separate “old site” or “modern site” products, and a classic-search visual grammar rather than copying Google branding.

The conversation then expanded into the local autonomous discovery idea. The user presented a plan where local machines would run for weeks to build index material. The assistant and user refined that idea into a governed “local autonomous discovery foundry” and then into a more product-facing contribution network. The key change was that local autonomy should not be a blind scraper swarm. Instead, it should be policy-governed: source discovery, demand discovery, source-cache building, candidate generation, evidence pack generation, review, and promotion gates. The principle emerged that anyone can help create candidates and evidence, but nobody can directly mutate public truth. This led to Eureka Nodes, WorkUnits, SearchNeeds, Candidates, Packs, Review, and Master Index as major product concepts.

Next, the conversation turned to website structure, domains, and capability negotiation. The user asked whether separate subdomains like old, files, and API should exist. The answer developed into a stable domain doctrine: use one canonical route space, with host aliases only as representation/profile selectors. `www` is the canonical human site, `api` is an API alias, `files` serves immutable artifacts, `old` forces legacy/read-only representation, and so on. The assistant emphasized that paths identify resources and hosts choose default representations. This reinforced the larger design principle that the source/evidence truth must not change because a browser is old.

The conversation then moved into monorepo structure and native clients. The user wanted short, sharp, long-lived directory names. The decision that emerged was to organize native clients by stable API/toolchain family rather than era or support status. The recommended native tree used `native/mac/carbon`, `native/mac/appkit`, `native/mac/swiftui`, `native/win/win16`, `native/win/win32`, `native/win/winforms`, and `native/win/winui`, with shared native libraries under `native/lib/c89`, `native/lib/objc`, and `native/lib/dotnet`. The rationale was that names like “legacy,” “modern,” “classic,” or “universal” decay as support status changes. Matrix files should carry OS versions, CPU architectures, toolchains, build hosts, and artifact names.

A major consolidation happened when the user asked for a recap of the entire conversation and a monorepo plan. The response organized the work into Track A, Track B, Track D, Track C, and Track E, with later expansion tracks. The user then accepted an execution order: Track A, then Track B, then Track D, then Track C, then Track E. The assistant later refined this by adding A0/preflight and quality gates. AIDE Lite then became central. The user described an AIDE Lite handoff and eventually reported that AIDE Lite had been synced into Eureka with commits and validations. The assistant generated the first post-handoff prompt, `EUREKA-AIDE-REAL-01`, and later `EUREKA-CONVERGE-01`. The user reported success after the repo-health task, and the conversation moved from syncing AIDE to generating actual Eureka implementation prompts.

As planning continued, the sequence was repeatedly updated to match new repo status. At one stage the plan was to run Track A, Manual Observation Batch 0, Track B, Track D, Track C, and Track E. Later, after the user reported that Track A and Track B were done, the plan moved toward IA metadata connector foundation, H0 Source Operating System, H1 metadata connector wave, extraction, ranking, packs, actions, snapshot/relay, hosting, native clients, and wider expansion. Later still, a new pivot occurred: after R0 runtime seams, the recommended route became LOCAL, HUNT, SYN, F, G, H, I, J, K, and then D/C/E/L. This pivot mattered because it introduced the local appliance as the integration surface. Future features should prove themselves through the local product rather than through isolated contracts.

The final visible phase of the chat focused on current branch state. The user pasted a May 16 status saying `main` had a better AIDE/control-plane baseline while `dev` had HUNT product work, and that `main` should be merged into `dev` before continuing. The assistant then checked the live repo via GitHub tools. It found that `main` and `dev` were diverged 13/13, that `main`’s latest task packet pointed to `Q62` with placeholder allowed paths, that `main`’s broad golden-task run failed 9 of 136 tasks, and that `dev` had HUNT-12 completed with warnings and SYN-00 queued. This led to the final operational conclusion: we are on track, but do not start SYN or F0 yet. First reconcile `main` into `dev`, green or classify the AIDE eval failures, resolve or classify HUNT warnings, produce a perfect HUNT closeout, then run promotion review and only then proceed to SYN-00.

## 3. Main Themes

### Eureka as an evidence-backed resolver rather than a normal search engine

The most persistent theme was that Eureka’s product identity is not a generic web search engine. It is an evidence-backed resolver for temporal digital objects. That distinction came up because the user repeatedly pushed for the “best possible search engine” and cross-era ecosystem. The conversation concluded that the strongest product unit is not a URL or a page, but a resolution packet or investigation state: interpreted intent, object candidates, evidence claims, identity clusters, compatibility notes, rights/risk posture, actions, absence reports, and confidence.

The larger consequence is that Eureka must preserve uncertainty instead of hiding it. It should return verified results, provisional candidates, near misses, known absences, policy-blocked records, and remaining work. This connects directly to later Search Hunt Sessions. A miss is not a dead end; it becomes a need, a WorkUnit, or an active investigation.

### One canonical truth, many representations

Another major theme was compatibility across machines and eras. The user wanted all kinds of hardware and software to access the search engine, product pages, wikis, links, integrations, backend, desktop apps, and accounts without splitting the system into arbitrary tiers. The conversation settled on capability negotiation, representation profiles, canonical view models, and semantic parity tests.

The conclusion was that there can be many representations—modern HTML, classic HTML, HTML 3.2-ish, text, file-tree views, JSON/API, snapshot, terminal, relay, native card—but they must preserve the same meaning. A renderer can simplify presentation, remove interactivity, or paginate aggressively. It must not remove identity, source posture, evidence posture, compatibility caveats, rights/risk caveats, actions, limitations, gaps, or absence scope.

### AIDE Lite as control layer, not product truth

The conversation repeatedly distinguished AIDE from Eureka product semantics. AIDE Lite became the repo-local control plane for compact task packets, review packets, repo snapshots, validation, queue continuity, and prompt discipline. The user reported successful AIDE sync and repo-health tasks. The assistant then used AIDE’s task packet approach as the basis for future Codex prompts.

The important conclusion is that AIDE metadata helps control the work, but product truth lives in Eureka contracts, runtime, accepted architecture docs, audits, and reviewed evidence. Generated AIDE state can become stale, as seen in the final branch comparison where a repo-health file claimed main/dev equality while live compare showed divergence. Future work must regenerate AIDE state after branch changes and must not treat generated packets as authoritative when they conflict with actual branch state or validation evidence.

### Local autonomy as governed foundry, not scraper swarm

The user was interested in running local machines for long periods, using local models and source probes to build a master index. The conversation accepted the ambition but rejected uncontrolled scraping or unbounded crawling. The model that emerged was a local autonomous discovery foundry and, later, Eureka Nodes. Nodes may create candidates, observations, evidence drafts, local review items, and packs. They may not mutate public truth.

This theme led to source policy registries, WorkUnits, candidate stores, source caches, evidence ledgers, local review queues, pack builders, and reviewed public-index rebuilds. The goal is to let agents do preparation while humans or policies handle approval, rights ambiguity, source policy, and review.

### Local appliance as the mandatory proof surface

The later pivot toward LOCAL/HUNT/SYN was one of the most important changes. Earlier plans moved from R0 runtime seams toward F0 extraction and other tracks. The user pasted a later plan arguing that F0 should wait and that the correct next phase was a Local Appliance/Search Hunt Workbench. The assistant agreed.

The conclusion was that the local appliance becomes the body of the product. Future features must prove themselves through it unless there is a specific reason they cannot. The local appliance includes an explicit instance root, local HTTP server, HTML workbench, WorkUnit queue, review/rebuild loop, deterministic workers, auto-test harness, LAN safety policy, clean-machine bootstrap, and closeout. This is the transition from specification repository to runnable local product.

### Search Hunt Sessions as the active investigation nervous system

Another central theme was the transformation of search into a resumable, steerable investigation. A Search Hunt Session can be created when indexed search is weak or absent. It records intent, checked layers, WorkUnits, sources checked, sources blocked, user steering, exhaustion reports, and future actions. It allows pause/resume/steer, background WorkUnit runners, deterministic replay, and eventually disabled-by-default AI escalation.

The conversation concluded that this is how Eureka becomes a “hive mind” without corrupting truth: search produces demand, demand produces WorkUnits, WorkUnits produce candidates, evidence supports candidates, review promotes records, and future users benefit.

### Branch synchronization and validation as product governance

The final theme was operational. As the repo became more complex, branch state itself became part of product quality. The chat ended with GitHub connector verification showing `main` and `dev` diverged 13/13. `dev` had HUNT work and a queued SYN-00; `main` had Q62/source-slice/AIDE state and failing broad golden tasks. Generated repo-health claims could not be trusted if they contradicted live branch comparison.

The final plan therefore shifted from starting SYN to doing `DEV-MAIN-AIDE-SYNC-01`, then AIDE eval repair/classification, warning zeroing, HUNT perfect closeout, promotion review, and only then SYN. This is a key lesson for the larger project: control-plane health is not clerical; it determines whether future work can safely proceed.

## 4. What We Were Actually Trying To Achieve

The explicit user goal was to consolidate a large body of planning into an optimal, executable plan for `julesc013/eureka`. The user wanted to know what had been discussed, what had been decided, how to structure the monorepo, how to generate prompts for GPT-5.5/Codex, and how to stay aligned as the repository evolved. Later, the user wanted to archive this chat so the reasoning and state could be preserved for a larger project book.

A second explicit goal was to avoid repeating mistakes. The user repeatedly asked whether the plan was the best possible, whether anything was missing, and whether the repo was on the right track. The user was concerned about drift: stale queue pointers, generated task packets not matching repo reality, old P-number plans conflicting with new track plans, and branches diverging. This drove the emphasis on AIDE Lite, convergence audits, task-state guards, idempotent WorkUnits, commit standards, and validation gates.

An inferred goal was to convert Eureka from a governance-heavy prototype into a real local product without sacrificing safety. The user’s later plans show a desire for autonomy: local machines searching sources, agents finding hard results, and the system rapidly improving. The assistant repeatedly constrained that ambition into governed steps: local appliance, Search Hunt Sessions, WorkUnits, policy-gated source probes, evidence review, and reviewed-index rebuilds. The user accepted this direction by continuing to paste and refine plans around LOCAL, HUNT, SYN, and the “autonomy may discover; review may promote” law.

The goals changed over time. At first, the focus was on the ultimate architecture, website design, and monorepo/naming structure. Then it moved to AIDE synchronization and prompt-generation discipline. Then it moved to current repo state, Track A/B completion, IA/H2 connector plans, Rust migration ideas, active hunt sessions, local appliance, and finally branch reconciliation before SYN. The main change was from visionary architecture to operational sequencing. The user’s question stopped being “what should Eureka become?” and became “given what the live repo says now, what exact next step keeps us on the optimal track?”

Several goals remain unresolved. The repo’s actual state must still be reconciled across `main` and `dev`. The failing broad AIDE golden tasks on `main` must be fixed or classified. The six HUNT warnings on `dev` must be resolved or accepted as non-product warnings. The user must decide whether promotion to `main` is desired before SYN or whether work may continue on `dev` after explicit review. More broadly, the future implementation of SYN, F0, G, H, I, J, D, C, E, K, and L remains unbuilt or not directly verified in this chat.

## 5. Decisions and Commitments

The first major decision was that Eureka should be treated as an evidence-backed temporal object resolver, not a conventional search engine or app store. This appears to be a stable decision because the user repeatedly carried it forward and incorporated it into later plans. The alternative would have been a normal query-to-pages search site or a downloader/app-store model. That alternative was rejected because it would not preserve provenance, absence reasoning, rights/risk posture, compatibility evidence, or investigation state.

A second decision was to use one canonical backend and route space with many negotiated representations. The user asked about supporting all machines without hard tiers, and the conversation settled on capability negotiation, profile aliases, canonical view models, and renderer parity. This decision remained stable through later phases, though the local appliance later became the immediate proof surface. A future revision could refine specific representations, but the core “same truth, many projections” principle should not be discarded without explicit review.

A third decision was to organize native clients by stable API/toolchain family. Names like `carbon`, `appkit`, `swiftui`, `win16`, `win32`, `winforms`, and `winui` were preferred over “legacy,” “modern,” or “desktop.” This decision was accepted in the monorepo planning phase. Its consequence is that changing support status belongs in matrix files, not directory names. It may be revisited only if the repository adopts a different native strategy or if an API family split becomes technically wrong.

A fourth decision was to use AIDE Lite as Eureka’s repo-local control layer. This was not a product feature decision; it was an operating decision. The user reported AIDE Lite handoff completion, repo-health report creation, and clean validations. The assistant then began generating Codex prompts around `.aide/context/latest-task-packet.md`, `.aide/reports/eureka-aide-lite-operating-handoff.md`, and AGENTS guidance. The consequence is that future prompts should not rely on giant pasted chat histories. However, the final branch-state discussion shows that AIDE-generated state must be regenerated and checked; it cannot override live repo evidence.

A fifth decision was to run work through tracks and gates rather than arbitrary prompts. The old P-number queue was reconciled into Track A, B, D, C, E, later F–L, and then later into LOCAL/HUNT/SYN as a product kernel. This decision evolved over time rather than being fixed from the beginning. The latest accepted ordering is more nuanced: because LOCAL and HUNT were reported/verified as present on `dev`, the current queue should focus on branch sync and HUNT closeout before SYN. The broader track order remains background doctrine.

A sixth decision was that local autonomy is allowed only as governed candidate/evidence production. The repeated law—autonomy may discover, candidates may propose, evidence may support, review may promote, only reviewed evidence-backed records become public truth—was accepted and preserved across many summaries. This is one of the most important commitments. It rejects blind crawler swarms, AI-as-truth, unreviewed index mutation, and public-query live fanout.

A seventh decision was to pivot from F0 extraction to LOCAL/HUNT/SYN. The user pasted a plan saying that R0 fixed the organs and LOCAL must build the body. The assistant agreed and expanded the plan. This decision superseded the earlier route of R0 → F0 → G/H/I/J/K/E. The new logic is that every future product feature needs a local appliance/workbench to prove behavior.

The final operational decision in this chat was that SYN should not start until `main` and `dev` are reconciled. This decision was grounded in a live GitHub compare in the chat showing branch divergence. The assistant recommended `DEV-MAIN-AIDE-SYNC-01`, `AIDE-EVAL-GREEN-01`, `AIDE-LEDGER-SIZE-01` if needed, `HUNT-WARNING-ZERO-01`, `HUNT-PERFECT-CLOSEOUT-01`, `HUNT-TO-MAIN-PROMOTION-REVIEW`, and then `SYN-00`. This decision is current at the end of the chat.

## 6. Rejected, Superseded, or Deprioritised Ideas

The idea of building Eureka as “just a search engine” was rejected early. It was considered because the public site should feel like search, but it was insufficient for the user’s goals. Eureka needs evidence, compatibility, source posture, absence reasoning, actions, review, and contribution loops.

The idea of separate modern/old/lite/mobile/API sites was rejected. It was considered as a way to serve different machines. It was superseded by one route space with many representations and profile/host aliases. This is likely final as a doctrine, though specific hosts or profiles may change.

The idea of copying Google’s style literally was rejected. A classic search grammar is acceptable; Google branding, logos, exact trade dress, or protected identity are not. The project should use “Temporal Minimal Search” or a similar neutral design language.

The idea of copying AIDE’s `.aide/` wholesale into Eureka was rejected. The correct approach was merge/adapt a repo-specific AIDE Lite pack. AIDE’s memory belongs to AIDE; Eureka’s `.aide/` must describe Eureka. This remains important because context contamination is a recurring risk.

The idea of starting broad autonomous live web crawling was rejected repeatedly. It may become source expansion later, but only through source policy, approved endpoints, fixtures, bounded metadata probes, source cache, evidence candidates, review, and quality audits. Bulk scraping, unbounded crawling, bypassing access controls, Reddit ingestion, and public-query live fanout were rejected as defaults.

The idea of doing all connectors before extraction/ranking was deprioritized. A later plan argued that too many sources before extraction/ranking would produce a broad but shallow system. The preferred route is to prove one connector pattern, build source OS, run limited metadata waves, then add extraction and search quality depth.

The idea of doing native clients before snapshots/relay was rejected. Native clients should consume contracts, snapshots, relay endpoints, and public envelopes, not unstable backend internals. This decision was later complicated by dev reportedly containing some C/D/E planning artifacts, but full native productization remains later.

The idea of hosting early was rejected as unsafe. Static sanity can happen early, but full hosted public alpha requires ops, rate limits, logs, takedown/rights/safety processes, launch evidence, non-claims, and kill switches. Public launch remains deferred.

The idea of starting F0 extraction immediately after R0 was superseded by LOCAL/HUNT/SYN. Extraction remains essential, but it should happen through the local appliance and Search Hunt WorkUnit system.

The idea of starting SYN immediately at the very end of the chat was temporarily blocked by branch divergence. Dev’s task packet says SYN-00 is next, but live branch comparison shows main/dev divergence and main AIDE eval failures. Therefore the immediate next task is synchronization, not SYN.

## 7. Rationale, Tradeoffs, and Design Logic

The visible design logic favored long-term trust over short-term capability. Eureka’s domain is risky: old software, archives, drivers, binaries, rights uncertainty, malware risk, broken links, community mirrors, and ambiguous compatibility. A fast but careless system could return wrong files, unsafe downloads, false officiality, or hallucinated evidence. The conversation therefore repeatedly chose slower evidence/review gates over immediate autonomy.

One tradeoff was breadth versus depth. Broad source expansion is tempting because it promises more results. But the plans increasingly emphasized that breadth without extraction, ranking, explanation, and review creates a shallow index. The best MVP needs some strong sources plus member discovery, explainable ranking, review-gated public index, and safe manifests/actions. This is why H2 and H3 source expansion should remain policy/fixture gated and why extraction and search quality matter.

Another tradeoff was compatibility versus security. The user wanted machines from old eras through future systems to use Eureka. The conversation concluded that old machines should not force the main service to weaken security. Use old-safe representations, static snapshots, plain text, local relay, and read-only HTTP/LAN modes. Write/auth actions should go through modern relay/device-token flows. This keeps old platforms useful without exposing secrets or weakening TLS/security policies.

A third tradeoff was documentation versus runtime proof. Early repo work was contract-heavy, which was appropriate for safety. Later, the conversation recognized a risk of becoming too document-heavy. The local appliance pivot was a response: future tasks should not be considered complete if they only add policies, examples, and validators. They need runnable behavior, persistent state where applicable, tests, audit evidence, and local workbench integration.

A fourth tradeoff was AIDE as control plane versus product dependency. AIDE Lite is valuable because it shrinks context, generates task packets, enforces validation, and helps control Codex. But AIDE is not product truth. This distinction prevents generated task packets from overriding product contracts or live repo state. The final branch divergence check demonstrates why this matters: a generated health file can become stale.

A fifth tradeoff was “perfect closeout” versus forward momentum. Dev’s HUNT state had no hard blockers and SYN could start according to generated health. But main/dev divergence and main golden-task failures were a serious operational risk. The recommended queue pauses product progression to reconcile branches and clear/control warnings. This may slow momentum, but it reduces the risk of losing work or starting SYN on stale context.

The user seemed to care most about rigor, future-proofing, not losing context, and avoiding half-finished work. The design logic therefore emphasized idempotency, task resumption, source-grounded docs, changelog-ready commits, warning disposition, closeout gates, fresh-clone proof, and exact next-task pointers.

If this context is misunderstood, future assistants might start broad source probes too early, treat HUNT warnings as irrelevant, start SYN on a diverged branch, merge generated state incorrectly, or flatten tentative long-term tracks into current commitments. The report preserves the correct hierarchy: current branch sync first, then HUNT closeout/promotion review, then SYN.

## 8. Current State at the End of This Chat

At the end of the chat, the live GitHub connector evidence showed `main` and `dev` diverged 13 commits ahead/behind each other. This is the most important operational fact. It supersedes any generated repo-health claim that the branches are equal. `main` head was shown as `73d8e9eb590f43a5554abe35f99345c57d4ec06c`, with merge base `7de5c8b708c2a75a82d2ab6fe55673634847c197`. This branch state means the next task should be branch/AIDE reconciliation, not new product work.

`main`’s latest task packet, as checked in this chat, pointed to `Q62 - Eureka Second Fixture Source Slice v0` and contained placeholder allowed paths. That indicates stale or misaligned control state on `main`. `main` also had a broad AIDE golden-task run with 127 of 136 passing and 9 failing. This was explicitly treated as eval debt that should be fixed or classified before “perfect” workflow closeout.

`dev`, by contrast, carried HUNT work. Its latest task packet pointed to `SYN-00 — Synthetic Query Foundry planning over Local Appliance`. Its repo-health file said `HUNT-12` was the last completed task, status `pass_with_warnings`, hard blockers zero, warnings six, SYN can start, F0 can resume but is not recommended, and provider calls, source probes, extraction execution, deployment, production readiness, and public launch readiness were all false. A HUNT closeout result similarly recorded HUNT track complete, all required capabilities implemented/tested, workbench smoke passed, deterministic replay passed, AI escalation disabled, source probes/extraction/provider calls/deployment not performed, and main promotion review required.

The HUNT warning disposition file said the remaining warnings did not block SYN/F0 planning, but main promotion review must recheck runtime leakage and generated artifact cleanliness. The warnings included AIDE optional references/branch-name warnings, external second-device LAN proof deferred, runtime leakage debt, historical HUNT validator queue sensitivity, full unittest discovery timeout, and pre-commit generated artifact drift.

The current settled operational plan is: do not start SYN or F0 yet. Run `DEV-MAIN-AIDE-SYNC-01` first. Then fix or classify the AIDE golden-task failures (`AIDE-EVAL-GREEN-01`), handle oversized AIDE ledger if still needed, clear or classify HUNT warnings, run HUNT perfect closeout, run promotion review, and only then start SYN-00. This is settled as the last assistant recommendation, based on live tool evidence in this chat. The user has not yet reported executing it.

What remains tentative is how exactly the branch merge will be performed, whether all 9 golden-task failures can be fixed or must be classified as non-product warnings, and whether HUNT warnings can be fully zeroed. It is also not yet determined whether promotion to `main` will be a fast-forward after reconciliation or require a different merge/promotion plan.

## 9. Future Work and Next Steps

The immediate next step is `DEV-MAIN-AIDE-SYNC-01`. It should merge or reconcile `main` into `dev`, preserve dev’s HUNT work, preserve main’s newer AIDE/source-slice baseline, regenerate stale AIDE context/report packets, and not mutate `main` yet. This matters because `dev` contains HUNT product work and `main` contains conflicting AIDE/source state. If this step is skipped, future SYN/F0 work may be based on stale or partial context.

After sync, `AIDE-EVAL-GREEN-01` should address the 9 failing broad golden tasks on main. The target should be 136/136 pass or exact accepted non-product classification. This matters because AIDE is now the control layer for Codex/GPT tasks. If its golden-task suite is failing, token-survival and task-packet quality claims are weakened.

If large AIDE file-quality ledger warnings remain, `AIDE-LEDGER-SIZE-01` should split, compress, or otherwise reduce the generated ledger. This is an operational hygiene task. It matters because large generated files create repo friction and may obscure important diffs.

`HUNT-WARNING-ZERO-01` should then clear or classify the six HUNT warnings. This matters because HUNT is complete enough to proceed, but promotion to main requires more than “non-blocking for SYN.” Promotion needs fresh warning disposition, generated cleanliness, and runtime leakage review.

`HUNT-PERFECT-CLOSEOUT-01` should produce a final HUNT state packet under the updated AIDE baseline. It should rerun relevant HUNT/LOCAL validators, HUNT workflow smoke, full or scoped unittest discovery as appropriate, architecture boundary checks, generated artifact cleanliness, runtime leakage audit, and AIDE checks. It should not perform source probes, extraction, provider calls, deployment, or public launch.

`HUNT-TO-MAIN-PROMOTION-REVIEW` should then decide whether dev can promote to main. Promotion should happen only if dev contains reconciled main, all hard gates pass, warning debt is zero or explicitly accepted, generated state is fresh, and the merge strategy is clear.

Only after that should `SYN-00` begin. SYN’s purpose is to build the Synthetic Query Foundry over the completed Local Appliance and Search Hunt proof surface. It should create query/eval pressure before extraction/source expansion resumes. It must not start F0 implementation, source probes, extraction, model/provider calls, deployment, or public launch readiness.

After SYN, F0 deep extraction should resume through the local appliance and HUNT WorkUnit spine. Then G ranking/explanation/search quality, H source expansion, I packs/federation, J actions/preservation, D snapshots/relay, C native clients, E hosting, K semantic/AI assist, and L wider clients follow according to gates and priorities. This long-term sequence remains planning doctrine, not yet executed within this chat.

## 10. Artifacts, Files, Prompts, and Outputs

Several artifacts were created or discussed within this chat.

The AIDE Lite handoff artifacts were reported by the user as completed, including `.aide/queue/EUREKA-AIDE-FINAL-HANDOFF-01/`, `.aide/reports/eureka-aide-lite-operating-handoff.md`, `.aide/queue/index.yaml`, `AGENTS.md` updates, and refreshed AIDE context/task/review/eval/routing/token/memory artifacts. These were not created by the assistant in this chat; the user reported their creation after Codex work. Their purpose was to make Eureka self-sufficient for future AIDE Lite / Codex work.

The assistant generated a Codex prompt for `EUREKA-AIDE-REAL-01 — Add Eureka AIDE Lite repo-health report`. The user later reported it passed, with commit `5f57af5 docs(aide): add eureka repo health report`. It added `.aide/reports/eureka-repo-health.md`, `.aide/reports/eureka-repo-health.json`, queue evidence, latest task/review packets, AIDE token/eval metadata, and queued `EUREKA-CONVERGE-01`. This matters because it was the first real bounded AIDE-driven maintenance task after handoff.

The assistant then generated the `EUREKA-CONVERGE-01 — Track and prompt queue convergence audit` prompt. Its purpose was to reconcile the current repo state, AIDE queue state, old P-number plan, and new Track A/B/D/C/E order. This prompt marked the transition from AIDE syncing to actual Eureka track execution. The user’s later messages imply that subsequent work moved far beyond this, but this chat did not include an explicit status result for `EUREKA-CONVERGE-01`.

The conversation discussed many plan artifacts: Track A/B/D/C/E plans, later Tracks F–L, AIDE queue/index files, current-state summaries, source policy packs, native matrix files, host profiles, representation profiles, WorkUnit contracts, Source Hunt Session contracts, and local appliance tasks. Many of these were proposals or later statuses pasted by the user; they are important source material for future book chapters but should not all be treated as implemented unless the chat explicitly reports or verifies implementation.

The GitHub connector outputs near the end of the chat are important artifacts in their own right. They showed `main...dev` divergence, `main` and `dev` latest task packet content, repo-health files, HUNT closeout results, HUNT warning disposition, queue index entries, and golden-task run summaries. These are the strongest current-state evidence in the visible chat.

This answer itself creates seven archive markdown files and a ZIP package in `/mnt/data`. Those files are the new archive artifacts for the chat.

## 11. Open Questions and Unresolved Issues

The most immediate unresolved issue is how `main` and `dev` will be reconciled. The chat recommends `DEV-MAIN-AIDE-SYNC-01`, but the task has not yet been executed in this transcript. It is unknown whether the merge will be clean, whether conflicts will occur, and whether dev’s HUNT work and main’s AIDE/source-slice baseline can be reconciled without remediation.

The second unresolved issue is the status of the 9 failing broad AIDE golden tasks on `main`. The chat verified that the run failed 9 of 136 tasks, but it did not inspect or resolve all failures. Some failures may be due to stale context or legitimate policy changes; others may require fixes. This must be resolved or explicitly classified before perfect closeout.

A third unresolved issue is whether the six HUNT warnings can be cleared. The warning disposition says they do not block SYN/F0 planning, but promotion review must recheck runtime leakage and generated artifact cleanliness. The exact status after branch reconciliation is unknown.

A fourth unresolved issue is the ultimate ordering of D/C/E relative to F/G/H/I/J/K after the local appliance and HUNT. Earlier plans placed D/C/E before later expansions; later plans moved D/C/E after J/K in some cases, with a caveat that D may move earlier for old-machine demos. The current branch-control task does not require resolving the entire long-term order, but a future roadmap should clarify it after SYN/F0/G progress.

A fifth unresolved issue is the extent to which current dev HUNT work is runtime versus generated/audit surface. The queue index and HUNT closeout say capabilities are implemented/tested, but this chat did not inspect source code paths in depth. Future closeout should verify runtime behavior locally.

A sixth unresolved issue is public hosting. The conversation repeatedly deferred hosting. It remains unclear when a public alpha should happen, but the rule is settled: no hosting before ops, non-claims, source/evidence boundaries, rate limits, logs, takedown/safety processes, and launch evidence.

A seventh unresolved issue is AI/semantic assist. The chat accepts AI as a bounded candidate generator later, but it remains disabled. Future work must define and validate AI escalation contracts before any model/provider calls.

## 12. Risks and Failure Modes

The largest risk is over-compression. This chat contains a long sequence of plans that changed over time. A future assistant might compress it into “next is SYN” and miss the live branch divergence and main golden-task failures. To avoid this, preserve the final operational queue and the fact that live branch comparison outranks stale generated repo-health.

Another risk is treating all plans as equal. Early IA/H2/F/G/D/C/E plans were valid at their stage, but later LOCAL/HUNT/SYN and branch-sync plans superseded them as immediate next steps. Future assistants should distinguish historical planning doctrine from current execution queue.

A related risk is treating assistant suggestions as user decisions. The user accepted many directions by continuing with them and reporting execution, but not every assistant proposal became a user decision. This report marks major accepted directions where the user clearly proceeded, and keeps later tracks tentative.

There is also a risk of treating generated AIDE files as truth. The final GitHub check showed that generated repo-health can become stale. Future work should use AIDE files as control metadata, not product truth, and should regenerate them after branch changes.

Another risk is unsafe autonomy. The user’s ambitions include agents searching, testing, indexing, and finding hard results. The chat repeatedly constrained this to policy-gated WorkUnits and reviewed evidence. Future assistants must not turn this into broad crawling, unbounded scraping, public-query live fanout, or AI-to-truth.

A further risk is losing the local appliance pivot. Without LOCAL/HUNT, later extraction/source/ranking tracks can become isolated backend features. The local workbench is supposed to be the integration and proof surface.

There is also a risk of premature hosting or native clients. Hosting and native clients were repeatedly deferred until local proof, snapshot/relay, and ops boundaries exist. Future assistants should not treat public alpha or native skeletons as the next step unless the sync/HUNT/SYN/F0/G/H work has reached appropriate gates.

Finally, there is a risk of merging this chat incorrectly into a larger project book. It overlaps with other chats about AIDE, Eureka, native clients, source connectors, and local appliance. When aggregating, preserve the chronological evolution and current-state correction rather than flattening all plans into one undated roadmap.

## 13. Larger Project Contribution

This chat contributes a major governance and product-kernel chapter to the larger Eureka/AIDE project. It captures the maturation from vision to operational planning: Eureka as resolver, AIDE as control plane, local appliance as product kernel, Search Hunt as investigation layer, and branch reconciliation as current gate.

Its unique value is that it records the point where the project stopped treating contracts and policies as sufficient completion. The local appliance/HUNT/SYN pivot is a major milestone. It also records a concrete example of repo-state truth overriding generated reports: main/dev divergence contradicted stale repo-health equality claims. That lesson should likely become a formal project doctrine.

The chat overlaps with other likely project chats about AIDE Lite, Track A/B implementation, H2 source families, R0 runtime seams, Rust migration, and local appliance execution. It may conflict with older chats that say IA-BUNDLE-01 or H2-BUNDLE-01 is the immediate next step. Those were correct at their time, but the visible final state here says the current next step is branch/AIDE reconciliation before SYN.

The chat should feed into future book sections on:
- “Search as resumable investigation”
- “Evidence before truth”
- “Local-first appliance architecture”
- “AIDE as control plane”
- “Why generated state is not truth”
- “Prompt queues as engineering governance”
- “From old-platform search to cross-era resolver”
- “How to keep AI/agents bounded”

Before formalizing as requirements, the project should verify current repo state again, especially after any branch merges or new commits. The GitHub data in this chat is time-sensitive and should be treated as accurate for the chat moment, not permanently current.

## 14. What To Remember

- Eureka’s durable identity is a local-first, evidence-backed artefact-resolution network, not a generic search engine, downloader, app store, or chatbot.
- The central governance law is: autonomy may discover; candidates may propose; evidence may support; review may promote; only reviewed evidence-backed records become public truth.
- AIDE Lite is a repo-local control layer for compact task packets, review packets, validation, and prompt discipline. It is not product truth.
- The local appliance became the mandatory integration surface. Future features should prove behavior through local runtime, persistent state, tests, audit evidence, and the workbench.
- Search Hunt Sessions became the model for hard search: indexed lookup first, then resumable investigation, SearchNeeds, WorkUnits, evidence, review, and replay.
- The latest verified branch state in this chat showed `main` and `dev` diverged 13/13. Do not trust stale repo-health claims of equality.
- `dev` carried HUNT-12 completed with warnings and SYN-00 queued. `main` had Q62 task packet state and failing broad golden tasks.
- The immediate next queue is not SYN and not F0. It is `DEV-MAIN-AIDE-SYNC-01`, then AIDE eval/warning/HUNT closeout tasks, then promotion review, then SYN.
- Public hosting, live source probes, extraction, model/provider calls, native clients, downloads, installs, uploads, accounts, telemetry, and public launch claims remain gated.
- Future assistants must preserve chronological status. Older plans are useful doctrine but not necessarily current execution state.

## 15. Final Plain-English Summary

This chat was a long planning and state-control conversation for Eureka, a project meant to become a local-first, evidence-backed resolver for archived and current digital artefacts. The user’s goal was not simply to design a search engine, but to build a durable, cross-era system that can answer hard questions about software, drivers, manuals, media, archived objects, compatibility, provenance, and absence. Over the course of the conversation, the project was repeatedly framed as a resolver and investigation engine rather than a normal query-to-pages search site.

The conversation moved through several layers of planning. Early material focused on the ultimate product: a public search surface, local resolver app, shared evidence network, relay, native clients, and optional AI. The public site should feel simple and search-like, but internally the backend should preserve evidence, candidates, compatibility, risk, rights, and absence. The user clarified that the repo was `julesc013/eureka`, which shifted the discussion toward concrete repo structure and implementation planning.

A major design decision was to avoid separate “old site,” “modern site,” “mobile site,” or “API site” products. Instead, Eureka should have one canonical route space and one evidence/object/action model, with many negotiated representations. Old browsers, text clients, JSON API consumers, snapshots, relays, and native cards should all preserve the same semantic meaning. This eventually became Track A: the representation and view-model spine.

Another major decision was to use AIDE Lite as a repo-local operating layer. The user reported successful AIDE handoff and repo-health tasks. AIDE helps shrink context, create task packets, review packets, validation summaries, and queue state. But the chat repeatedly emphasized that AIDE is not product truth. Product truth lives in accepted Eureka contracts, runtime, architecture docs, audits, and reviewed evidence. The final branch comparison proved why this distinction matters: generated repo-health can become stale.

The conversation then developed Eureka’s contribution and autonomy model. Local machines and agents may help discover needs, source leads, candidate records, evidence candidates, and packs, but they may not mutate public truth. This led to Eureka Nodes, WorkUnits, SearchNeeds, Candidate Store, Source Cache, Evidence Ledger, Review Queue, Pack Builder, and reviewed public-index rebuilds. The core law became: autonomy may discover; candidates may propose; evidence may support; review may promote; only reviewed evidence-backed records become public truth.

As the project evolved, the plan pivoted again. Instead of moving directly from runtime seams into deep extraction, the better route became the Local Appliance and Search Hunt Workbench. This was a major change. The project needed a runnable local product kernel: initialize a local instance, start a localhost service, open an HTML workbench, search reviewed index, create Search Hunt Sessions, queue WorkUnits, review evidence, rebuild index, and run smoke/eval suites. Future extraction, ranking, source expansion, packs, actions, AI, relay, native clients, and hosting should prove themselves through this local appliance.

The Search Hunt concept was another key result. A hard search should not end at “no results.” If the answer is not in the index, Eureka should start a governed hunt: record the query, create a SearchNeed, queue WorkUnits, run bounded probes, produce candidates, create evidence, allow review, and eventually improve the index. This is how Eureka becomes an evidence-producing investigation system rather than a static search box.

The latest stage of the chat became operational. The user pasted status saying main had the better AIDE/control-plane baseline and dev had HUNT work, and that the next move should be to merge main into dev before continuing. The assistant checked the live GitHub state in the chat and found that `main` and `dev` were diverged 13/13. `main`’s latest task packet pointed to Q62 and had placeholder allowed paths; `main` also had a broad golden-task run with 127 passing and 9 failing. `dev` pointed to SYN-00 and had HUNT-12 complete with warnings, hard blockers zero, and source probes, extraction, provider calls, deployment, and public launch all disabled. Therefore the current correct next step is not SYN, F0, source expansion, or hosting. It is branch/AIDE reconciliation.

The final recommended queue is: `DEV-MAIN-AIDE-SYNC-01`, then `AIDE-EVAL-GREEN-01`, then `AIDE-LEDGER-SIZE-01` if needed, then `HUNT-WARNING-ZERO-01`, then `HUNT-PERFECT-CLOSEOUT-01`, then `HUNT-TO-MAIN-PROMOTION-REVIEW`, then `SYN-00`. This ordering matters because starting new product work on a diverged branch would recreate the recovery cycles the project is trying to avoid. The repo is on track, but synchronization and closeout discipline must precede the next product phase.

The main thing to preserve from this chat is the evolution of the plan and the final operational correction. Older plans about IA connectors, H2 packages, local appliance, F0 extraction, and broad source expansion remain valuable background doctrine. But the current execution state, according to the visible GitHub connector evidence in this chat, is branch reconciliation before SYN. Future assistants should not flatten all the plans into one undated roadmap. They must preserve which plans were historical, which were superseded, and which are current.

# Reader Status

- Chat title: Eureka Planning, AIDE Control, Local Appliance, and Search Hunt Workbench
- Report type: human-readable archive report
- Main value of this chat: It preserves the evolution from high-level Eureka architecture to current branch-control and HUNT/SYN execution planning.
- Most important decision: Do not start SYN/F0 yet; reconcile `main` and `dev`, green/classify AIDE evals, clear HUNT warnings, and run promotion review first.
- Most important unresolved issue: The live branch divergence and AIDE golden-task failures need to be resolved.
- Most important next action: Run `DEV-MAIN-AIDE-SYNC-01`.
- Safe for aggregation: with caveats
- Main caveats: Some repo-state facts are time-sensitive; older plans were superseded; generated AIDE health reports may be stale; this report uses only visible chat contents and tool outputs from this chat.
