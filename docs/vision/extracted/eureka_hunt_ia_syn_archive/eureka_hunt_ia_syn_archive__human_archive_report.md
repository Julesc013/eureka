# Human Archive Report — Eureka HUNT, IA, SYN, and Artefact Resolution Planning

Date anchor: 2026-05-31 Australia/Melbourne  
Scope note: This report uses the visible contents of this chat. Where the chat quotes repo-health reports, branch comparisons, generated task outputs, or earlier execution summaries, those are treated as facts about what was stated in the chat, not as newly re-verified repository facts unless the visible transcript included an explicit verification call. Several earlier turns were represented by pasted summaries or “skipped” transcript sections; this report does not claim access to hidden chain-of-thought or omitted messages.

## 1. Orientation

This chat was mainly about turning Eureka from a drifting, scaffold-heavy project into a disciplined, local-first artefact-resolution system with a credible path toward production. The conversation began from the user’s concern that a long series of generated tasks and bundle prompts had been “blitzed” through without necessarily producing production-ready code or a real product. That concern set the tone for the entire chat: the user wanted to stop accepting generated contracts, audit packs, queue entries, and validation boilerplate as a substitute for working software. The chat therefore became an extended strategic, operational, and architectural effort to define what “real” meant for Eureka: runnable local behavior, persistent stores, evidence-backed records, review gates, local HTML workbench proof, tests, replay, safe source policy, and explicit non-claims.

The central project throughout the chat was Eureka. Within the visible transcript, Eureka is described as a project that should find hard-to-resolve artefacts: old software, drivers, manuals, hidden archive members, frontier-resolution historical media, demo tapes, source packages, documentation, and other culturally or technically meaningful objects whose identity and best access path are scattered across weak metadata, archives, old uploads, format histories, and source collections. The chat repeatedly widened the product identity from “search engine” toward “universal artefact-resolution engine.” That shift matters. The user did not want a generic web search wrapper, a crawler, a downloader, or an AI answer machine. They wanted an evidence-first system that can start from a messy query, resolve intent, search what it already knows, begin a governed hunt when it does not know, generate durable SearchNeeds and WorkUnits, collect source observations, create evidence candidates, review them, and only then project reviewed records into a local or public index.

A major pressure in the conversation was repository health and branch/control-plane drift. The visible transcript contains multiple status reports and planning prompts around `main` and `dev`. At different moments, the chat discussed `dev` being ahead of `main`, `main` having newer AIDE control-plane updates, `dev` containing HUNT/search work, and the need to reconcile branches without losing either lineage. Some generated repo-health files were described as stale or contradictory when compared with branch state. This produced a strong rule: generated AIDE state is useful control metadata, not product truth; validated repo state and live branch comparison outrank stale generated reports. That rule became a recurring safeguard against future confusion.

The conversation also introduced a staged development path. First came recovery and local product grounding: R0 recovered production seams such as source observation, source cache, evidence ledger, review queue, and reviewed public index. LOCAL made the project runnable as a local appliance with an instance root, local HTTP service, HTML workbench, workunit queue, deterministic workers, local tests, and LAN read-only posture. HUNT then turned search into a workflow: Search Hunt Sessions, commands and steering, exhaustion reports, SearchNeeds, WorkUnits, background deterministic workers, workflow smoke tests, agent research task records with provider execution disabled, deterministic replay, and a disabled AI escalation gate. PLAY was later added as a bridge to make the local workbench feel useful. IA then became the first real source-family proof, with an Internet Archive metadata-only pilot that, according to the visible status reports, reached reviewed local index proof on `dev`.

The chat’s later part asked whether this could become something more general and intelligent. The answer that emerged was yes: Eureka should become a general artefact-resolution engine with domain packs, SYN as an evaluation and query-pressure foundry, SCOUT as a relation-guided discovery layer, F as safe hidden-member extraction, G as ranking/explanation, H as governed source expansion, I as packs/federation, J as actions/preservation, K as semantic and AI assist, D/C/E as snapshots, clients, and hosting, and L as wider ecosystem. A particularly important example was “frontier-resolution observational media,” such as early HDTV or D-Theater footage of ordinary life. The user saw this as exactly the kind of obscure but meaningful object Eureka should be able to resolve. The chat treated that not as a diversion, but as evidence that Eureka’s real domain is broader than old software.

The main outcome of the chat is not one final prompt or one file. It is a layered roadmap and a set of hard engineering invariants. Eureka should proceed from canonical baseline and local playability to IA source proof, synthetic/eval pressure, domain modularity, relation-guided discovery, safe extraction, ranking, source expansion, packs, actions, AI assistance, snapshots, native clients, hosting, and finally production. The near-term conclusion was that the current IA metadata pilot on `dev` appears to be a major breakthrough but not yet a production or public-hosted system. The user’s desired “enter a query and see Internet Archive results come through the local HTML page” should be implemented as progressive result lanes: reviewed local index first, candidate/source cache next, bounded IA metadata search, item metadata and file manifest inspection, evidence candidates, review, reviewed index rebuild, and deferred extraction through F0 gates. This is the visible path from local workbench to a real self-improving artefact discovery system.

## 2. The Story of the Conversation

The conversation opened with a problem: the user believed prior task execution had produced too much scaffolding and not enough working product. They described Codex or task execution as having “blitzed” through prompts without turning the series into production-ready code. The user wanted to interrupt the existing plan, repair the accumulated work, and create a future prompt/task system that would not require repeatedly going back to finish half-done foundations.

The first major direction was recovery. The visible transcript includes long reasoning about R0-like remediation: auditing the dev branch, quarantining task-shaped runtime leakage, cleaning contract taxonomy, reconciling generated artifact drift, and retiring legacy runtime architecture leakage. The important theme was that prompt/task/audit vocabulary had leaked into runtime architecture. This was treated as a serious smell. Runtime modules named after H-series bundle waves, fixture-only modules posing as runtime, `truth_boundary` and `product_boundary` payloads embedded in product code, and validators that only proved artifact existence were all discussed as failure modes. The recommended correction was not a rewrite in Rust or a scorched-earth reset, but a production-reality recovery pass: classify artefacts, quarantine prompt-shaped runtime, create real domain seams, and prevent future runtime contamination.

The chat then moved into LOCAL. After R0 established real persistence and review/index seams, the user wanted the project to become runnable on a machine. The plan forked away from F0 extraction into a Local Appliance / Local Network Workbench track. The purpose was to make Eureka locally hostable before future expansion. The LOCAL track introduced explicit instance layout, local HTTP service, HTML search/object/absence workbench, operator-gated WorkUnits, source probe runner boundaries, review/index rebuild from UI, deterministic local agent/worker runner, auto-test/auto-search harness, LAN safety, LAN smoke testing, clean-machine proof, and closeout. The rationale was straightforward: future extraction, ranking, connectors, and AI work should be grounded in a local product surface, not just validators and audit reports. The user proceeded through the generation of many LOCAL prompts and status reports.

The next major chapter was HUNT. The user and assistant developed the idea that search should not be a single request-response but a resumable investigation. The HUNT series defined and sequenced Search Hunt Sessions, UI state, pause/resume/steer commands, exhaustion reports, SearchNeeds, WorkUnits, background deterministic workers, integration smoke tests, agent research task records with providers disabled, deterministic replay, an AI escalation gate that remained disabled by default, and a closeout/handoff. The user repeatedly requested “Next,” and the chat generated full prompt packets for HUNT-01 through HUNT-12 and remediation/promotion tasks. Even though these prompts were long, their common design logic was consistent: each step added one bounded product capability, explicit state, CLI/API/UI proof, tests, validators, audit evidence, and strict boundaries against source probes, extraction, model calls, downloads, deployment, and unreviewed truth mutation.

While this was happening, branch and AIDE control-plane issues became prominent. The transcript shows discussion of `origin/main` and `origin/dev` being diverged at one point, with `main` containing a newer AIDE/control-plane/source-slice baseline and `dev` containing HUNT work. The user pasted a planning prompt for reconciling `main` into `dev` without promoting `dev` into `main`. The assistant verified or accepted the comparison in the visible transcript and produced `DEV-MAIN-AIDE-SYNC-01`: a careful merge/reconciliation task that preserved `main`’s AIDE baseline and `dev`’s HUNT product work. The later queue added AIDE-EVAL-GREEN-01, AIDE-LEDGER-SIZE-01, HUNT-WARNING-ZERO-01, HUNT-PERFECT-CLOSEOUT-01, and HUNT-TO-MAIN-PROMOTION-REVIEW. This sequence aimed to make AIDE golden evals pass, reduce oversized generated reports, clear warnings, perfect HUNT closeout, and promote the baseline only if gates passed. These tasks were not product features; they were quality and canonicalization steps.

The conversation then broadened product identity. The user introduced a detailed reflection on a 1993 New York D-Theater/D-VHS clip and a broader category of “frontier-resolution observational media” or “advanced-format everyday-life documentation.” The chat treated this as a strong Eureka use case. This expanded Eureka’s mission from software/driver discovery into cross-domain artefact resolution: resolving provenance, format lineage, representation quality, upload history, uncertainty, related objects, and best access paths. The conversation concluded that this media class should become a formal query/domain family, not a replacement for the software wedge but a second wedge that exercises different parts of the engine.

Following that, the chat synthesized a larger architecture: Universal Artefact Resolution Engine. The discussion introduced domain packs as a way to generalize without hardcoding every category. A domain pack would define object types, source families, identifier patterns, metadata fields, compatibility or format rules, risk/rights policy, query examples, eval sets, and renderer hints. Proposed packs included legacy software, drivers/support media, frontier-resolution media, manuals/docs/scans, package/source releases, and later many more. This led to a revised roadmap: canonicalize, PLAY, IA metadata pilot, SYN foundation, DOMAIN packs, SCOUT relation-guided discovery, SYN integration, IA source loop completion, F extraction, then G/H/I/J/K/D/C/E/L.

The user later reported or pasted a status indicating that dev had advanced: LOCAL + HUNT + PLAY + first real IA metadata source vertical slice existed on `dev`, IA metadata live probe had succeeded with two HTTPS requests, IA source cache/evidence/candidate/review/reviewed-index stages had passed, and the current recommended task was SYN-00. The assistant checked a GitHub comparison in the visible transcript and reported `dev` ahead of `main` by 22 commits, with many IA/PLAY queue and audit files. The conclusion shifted again: the branch/control crisis seemed resolved earlier, but now the IA pilot baseline on `dev` needed promotion review before becoming canonical on `main`.

At the end, the user asked for the ultimate forward plan and expressed a specific desired product behavior: spin up a local HTML page, enter a query, search the entire Internet Archive deeply, and see results come through progressively from local index, source cache, metadata, files, archives, subdirectories, and packaged files. The assistant reframed that goal as a progressive, budgeted IA artefact-resolution connector rather than a synchronous full crawl. The final design described search lanes: reviewed local index, local candidate index, IA source cache, live IA metadata search, item metadata and file manifest inspection, review queue, reviewed index update, and deferred deep extraction. The important distinction was that “deep IA search” should mean progressive deepening from evidence and intent, with no downloads, no broad crawling, no arbitrary fanout, no automatic truth, and extraction deferred to F0 policy gates.

## 3. Main Themes

### From scaffolding to product reality

The most persistent theme was the need to stop mistaking scaffolding for product. The user repeatedly pushed against generated plans, prompts, validators, and audits that did not result in usable software. The chat responded by defining progressively stricter completion standards: runtime behavior, persistent state, CLI/API/UI proof, tests, negative tests, validators, audit evidence, local workbench proof, regression/eval coverage, and no forbidden side effects. This theme connects to the larger project because Eureka is large enough that generated control-plane artifacts can easily become self-referential. The conversation’s answer was to make product proof run through the local appliance and HUNT workflow.

### Local-first architecture

A second theme was local-first operation. The system should be able to run on the user’s machine before public hosting. The local instance layout, local HTTP server, HTML workbench, operator token, reviewed local index, WorkUnits, local deterministic workers, smoke tests, LAN read-only mode, and clean-machine proof were all meant to create a working local product kernel. This mattered because future extraction, source connectors, and AI should be observable and testable through a real interface, not only through scripts or audit packs.

### Search as investigation

The HUNT work established a conceptual shift: Eureka search should not end with “no results.” A miss should become a structured, replayable investigation. This theme introduced Hunts, exhaustion reports, SearchNeeds, WorkUnits, steering, background workers, replay, and AI escalation boundaries. It connects directly to the user’s long-term ambition for Eureka: the system should compound knowledge, turn misses into work, and make future users benefit from previous failed or partial searches.

### Evidence-first source integration

The IA metadata pilot and the larger IA connector plan show another theme: external sources must not become truth. The system should collect source observations, normalize them, create evidence candidates, queue review, and only then rebuild the reviewed local index. This principle applied to IA metadata and was projected forward to Wayback, GitHub, package registries, Software Heritage, Wikidata, Open Library, and other source families. The same logic also governs future extraction and AI.

### General artefact resolution

The conversation widened Eureka beyond software and drivers. The frontier-resolution media discussion showed that Eureka’s true object is not one domain but the hard-to-resolve artefact. The general engine should resolve identity, lineage, representations, provenance, uncertainty, evidence, actions, and future work. Domain packs became the mechanism for adding new areas without corrupting the kernel.

### Governance and branch discipline

AIDE and branch-state discipline were major themes. The user wanted a way to prevent future drift, stale generated health files, and branch divergence from misleading the project. The chat therefore produced a sequence of AIDE and promotion tasks that treated branch reconciliation as product quality work. AIDE was described as a control plane, not product semantics. This theme matters because without stable governance, the project will keep losing track of what is real, current, stale, or merely generated.

### Progressive IA deep search

The final theme was the desired end-user experience for Internet Archive search. The user wants a local HTML page where they can type a query and see results appear progressively while deeper searches run. The chat concluded that this is achievable if implemented as lanes and budgets: local reviewed index first, cached candidates and source cache next, bounded live metadata query, top item metadata, file manifests, evidence candidates, review, reviewed index rebuild, and eventually F0 extraction for hidden members. This is one of the most concrete future product goals from the chat.

## 4. What We Were Actually Trying To Achieve

The explicit user goal changed shape over the chat but remained consistent in spirit: make Eureka real. At first, that meant repairing a repo that had accumulated too much scaffold. Later, it meant building a local appliance, HUNT workflow, and IA source pilot. At the end, it meant turning Eureka into a complete progressive artefact search and discovery engine, starting with Internet Archive.

The inferred goal was stronger: the user wants a durable methodology for building ambitious software with AI/Codex without falling into prompt-generated illusion. They want each task to be one-shot or two-shot, complete end-to-end, validated, committed, and not require future rework because it was only superficially done. They also want a project memory/archive that can feed a larger book and specification corpus.

The goals changed as the repo state changed. Earlier the goal was recovery. Then it became local playability. Then HUNT closeout. Then branch/AIDE synchronization. Then IA source proof. Then SYN/DOMAIN/SCOUT/F planning. Finally, the user asked for the ultimate plan to search the entire Internet Archive deeply from a local page. The direction did not reverse; it layered.

The unresolved goal is public stable hosted production. The chat produced a full path but did not claim it is near. Production still requires hosting architecture, abuse controls, observability, backups, rollback, security review, source policy enforcement, public API stability, larger reviewed corpus, ranking/explanation quality, takedown/rights workflows, and operator/incident processes.

## 5. Decisions and Commitments

The most important decision was to treat Eureka as a local-first artefact-resolution engine rather than a generic web search tool. This was accepted implicitly through repeated user continuation and later explicit desire for a local HTML page. The decision depends on Local Appliance, HUNT, and reviewed-index foundations. It could be revisited only if the product direction changes away from local operation, which would contradict much of this chat.

A second decision was to put branch/AIDE canonicalization before SYN/F0 when `main` and `dev` were diverged. This was based on visible branch-state discussions. It was later superseded by a newer visible state in which the chat reported IA/PLAY work on `dev` and suggested IA promotion review. The underlying rule remains: repo branch state is part of product quality.

A third decision was that HUNT is the active investigation spine. Searches should create Hunts, exhaustion reports, SearchNeeds, and WorkUnits rather than dead ends. This appears settled as a product architecture decision. It underlies SYN, IA, F, G, H, K, and future UI work.

A fourth decision was that AI remains disabled/candidate-only until later gates. The chat repeatedly forbade model/provider calls, AI execution, and direct AI truth mutation. This is settled for current work but will be revisited in K or a later AI escalation gate.

A fifth decision was that IA is the first real source family. The visible final state says an IA metadata pilot exists on `dev`, and the user wants full IA deep search. The decision is not to build “full IA crawling” immediately, but to extend the metadata pilot into progressive IA result lanes.

A sixth decision was to add PLAY before large SYN. This was recommended because the reviewed local index is sparse and SYN needs real behavior to evaluate. The user did not explicitly reject this; later pasted synthesis treated it favorably. It remains a strong but still implementation-dependent decision.

A seventh decision was to add DOMAIN and SCOUT before or around F. DOMAIN makes the engine general, and SCOUT enables relation-guided discovery. This is more tentative than HUNT or IA because it is roadmap-level, not yet executed.

## 6. Rejected, Superseded, or Deprioritised Ideas

A full Rust rewrite was discussed earlier as not the right immediate move. The reason was that rewriting messy architecture in Rust would preserve the wrong shapes. The accepted order was to clean seams, establish a Python oracle, and only port stable seams later. This is temporary, not permanent; Rust may become relevant for performance-critical components later.

Continuing straight into F0 extraction was repeatedly deprioritized. Initially, F0 was blocked by production-reality concerns; later, it was deferred behind LOCAL, HUNT, PLAY, IA, SYN, DOMAIN, and SCOUT. Extraction remains important but should be driven by WorkUnits, SYN pressure, and domain packs.

Starting SYN immediately after HUNT was also temporarily deprioritized in favor of PLAY and IA. The reason was that synthetic evaluation is more useful when there is a local product corpus and a real source loop to test. SYN remains the next major quality engine, not rejected.

Uncontrolled open-web search, broad crawling, live fanout for every public query, forum scraping, downloads, install/execute actions, and AI browsing were consistently rejected for current phases. These may return only as policy-gated, budgeted, reviewed, and domain-specific future capabilities.

Treating generated AIDE state as product truth was rejected. The chat repeatedly emphasized that generated task packets, repo-health files, and audit outputs can be stale. Product truth must live in runtime, contracts, accepted docs, tests, and evidence.

Building a marketplace/app-manager/native ecosystem soon was deprioritized. The chat estimated those product classes as far away because they require actions, packaging, safety, rights, downloads, install policies, native clients, hosting, and trust infrastructure.

## 7. Rationale, Tradeoffs, and Design Logic

The conversation’s design logic is conservative about truth and aggressive about workflow. Eureka should be ambitious in what it tries to resolve, but cautious about what it claims. This leads to a tradeoff: the system may feel slower or more bureaucratic than a search engine because candidates must pass through evidence and review, but it gains trust, replayability, and long-term compounding value.

Another tradeoff is local-first versus hosted-public-first. Local-first delays public reach but makes the product testable, safe, and operator-controlled. The chat repeatedly chose local proof before hosting because public hosting introduces rate limits, abuse, privacy, source ToS, monitoring, incident response, and legal/rights workflows.

A third tradeoff is synthetic pressure versus fake evidence. SYN is valuable only if it tests behavior without fabricating truth. The chat therefore insisted that synthetic queries may create demand, expected behavior, SearchNeeds, and WorkUnits, but not evidence, verified records, hashes, compatibility facts, rights claims, or safety claims.

A fourth tradeoff is progressive IA deepening versus “search all of IA.” The user wants complete Internet Archive discovery. The chat reframed “complete” as a staged architecture: local index, cache, bounded metadata, item metadata, file manifests, review, reviewed index, and deferred extraction. This avoids abusive crawling and makes the UI progressively useful.

A fifth tradeoff is generic engine versus domain-specific usefulness. A purely generic engine risks being vague; a hardcoded software finder risks being narrow. Domain packs solve this by keeping the kernel generic while allowing domain-specific object types, metadata fields, source families, policies, and evals.

If future assistants misunderstand the context, several things could go wrong: they might start SYN before canonicalization, enable source probes too early, treat IA metadata as truth, build extraction as standalone archive tooling, implement AI browsing as a shortcut, or flatten the roadmap into generic search-engine tasks. The conversation’s design logic rejects all of those.

## 8. Current State at the End of This Chat

The end-of-chat state is mixed between visible claims and unverified execution state. As visible chat content, the latest pasted synthesis says Eureka on `dev` has Local Appliance, HUNT, PLAY, and a first real IA metadata vertical slice through reviewed local index proof. The assistant used a GitHub compare call during this chat and reported `dev` ahead of `main` by 22 commits. That means the latest IA/PLAY work is described as real on `dev`, but not canonical on `main`.

The settled product state is that Local + HUNT is the project’s local investigation spine and IA metadata is the first source-family proof. The settled future direction is to build progressive IA search lanes, SYN evaluation pressure, domain packs, SCOUT relation discovery, F extraction, G ranking/explanation, H source expansion, I packs/federation, J actions/preservation, K AI assist, D snapshots/relay, C native clients, E hosting, and L wider ecosystem.

The tentative state is whether IA should be promoted to main before SYN or whether SYN can proceed on `dev`. The visible assistant recommendation was to promote IA pilot baseline to main first if gates pass, then start SYN. The user did not yet request the next exact prompt after this final IA plan.

The unresolved technical question is how much of IA deep search is already implemented versus still planned. The chat states an IA metadata pilot exists; it does not establish that progressive IA streaming/search lanes, item file manifest UI, collection discovery, full review-from-page flows, or F0 extraction of IA files are already built. Those are future work.

The next best action emerging from the final discussion is likely an IA promotion review or an IA-DEEP-00 planning prompt, depending on whether the user wants canonicalization first or immediate dev-lane expansion.

## 9. Future Work and Next Steps

The first priority is canonicalization if the project wants main to represent the current baseline. The visible state says `dev` is ahead of `main` by 22 commits. An IA-TO-MAIN-PROMOTION-REVIEW should validate IA/PLAY/HUNT/LOCAL state, run tests and safety gates, and promote only if all gates pass.

The second priority is IA-DEEP planning. IA-DEEP-00 should design the progressive IA search connector: local reviewed index lane, IA source-cache lane, live IA metadata lane, item metadata lane, file manifest lane, candidate/evidence/review lane, reviewed-index update lane, and deferred extraction lane. This should produce a staged plan, policies, budgets, UI/API event model, and replay harness.

The third priority is IA progressive search implementation. IA-DEEP-01 through IA-DEEP-09 should build live search lanes, source-cache integration, item metadata fetch, file manifest normalization, streaming/polling event updates, candidate/evidence/review UI, reviewed-index rebuild from page, replay harness, and closeout. These tasks must not download files or perform extraction.

The fourth priority is SYN. SYN should be built after there is enough PLAY and IA behavior to test. It should define query taxonomy, eval contracts, deterministic seed datasets, mutation/dedup, policy/adversarial filters, eval split manager, HUNT regression, SearchNeed and WorkUnit seeders, latency/load harness, demo query curation, and closeout.

The fifth priority is DOMAIN. Domain packs are required for generality. They should start with software, drivers/support media, frontier-resolution media, manuals/docs/scans, and package/source releases.

The sixth priority is SCOUT. It should add relation-guided candidate discovery, discovery trails, source trust, review feedback, and WorkUnit integration while staying fixture/local and candidate-only.

The seventh priority is F0 extraction. It should be driven by HUNT/SYN/DOMAIN/SCOUT and should prove safe hidden-member discovery through the workbench, source observation, evidence candidates, review, and reviewed index.

Beyond that, G/H/I/J/K/D/C/E/L continue the path toward a public stable product, but they depend on the earlier gates.

## 10. Artifacts, Files, Prompts, and Outputs

The chat generated a very large number of prompt packets. The most significant are not individual filenames but families of prompts.

The R0 and remediation prompts were concerned with production-reality recovery: contract taxonomy cleanup, generated artifact drift, runtime leakage, promotion review, and preventing prompt vocabulary from becoming runtime architecture. These should be preserved as background for the project’s quality doctrine.

The LOCAL prompt series defined the local appliance: instance layout, local server, workbench, WorkUnit queue, workers, LAN safety, smoke tests, and closeout. These are central to the project.

The HUNT prompt series is one of the most important artifacts in this chat. It specifies Search Hunt Session runtime, UI, commands, exhaustion reports, SearchNeeds, WorkUnits, background runner, workbench integration smoke, agent research task boundary, replay, AI escalation gate, closeout, remediation, warning-zero, perfect closeout, and promotion review. These prompts are source material for a future HUNT chapter or spec.

The AIDE prompts—DEV-MAIN-AIDE-SYNC-01, AIDE-EVAL-GREEN-01, AIDE-LEDGER-SIZE-01, HUNT-WARNING-ZERO-01, HUNT-PERFECT-CLOSEOUT-01, HUNT-TO-MAIN-PROMOTION-REVIEW—represent the governance and quality-control side of the project.

The PLAY and IA prompts and status reports mark a transition into product usefulness. PLAY creates a seed corpus and demo workflows; IA creates the first real metadata source loop.

The SYN, DOMAIN, SCOUT, and F roadmaps are future architecture. They should be treated as design material rather than completed implementation.

The frontier-resolution media passages are important conceptual artifacts. They define a second domain wedge that can become a formal domain pack.

The final IA deep search design is an important future-product artifact. It defines the desired local page behavior and progressive result lanes.

## 11. Open Questions and Unresolved Issues

The first unresolved issue is the exact current repository state. The visible transcript includes a GitHub compare showing `dev` ahead of `main` by 22 commits, but this report does not re-verify after the final user prompt. A future assistant should verify branch state before producing execution prompts.

The second issue is what has been promoted to `main`. The chat states IA/PLAY/HUNT work exists on `dev`, but not canonical on `main`. This affects whether SYN should start from `main`, `dev`, or after promotion.

The third issue is whether AIDE evals, report sizes, warnings, and HUNT perfect closeout are fully green in the actual repo. The visible transcript reports various green states at different times, but generated state can be stale. Future work must run validators.

The fourth issue is how far IA deep search has been implemented. The pilot is described as complete through reviewed local index proof, but progressive search page lanes, streaming events, file manifest UI, collection discovery, and extraction bridge are future work.

The fifth issue is public hosting readiness. The chat repeatedly says production/public launch readiness is false. Public stable production remains a long roadmap.

The sixth issue is user preference between immediate IA-DEEP expansion on `dev` and promotion to `main` first. The assistant recommended promotion review first, but the user’s final request focused on ultimate plan and IA search experience, not a final operational choice.

## 12. Risks and Failure Modes

The biggest risk is over-compression. This chat contains many roadmap layers, and compressing it to “do SYN next” would lose PLAY, IA, DOMAIN, SCOUT, and the progressive IA design.

Another risk is treating assistant brainstorms as final user decisions. Some plans were accepted implicitly by continuation, but not every suggested task was executed or formally approved.

A third risk is stale repository claims. The chat itself shows generated repo-health state can contradict branch comparison. Future assistants must verify live repo state.

A fourth risk is enabling unsafe behavior too early. The user wants deep IA search, but the correct system forbids broad crawling, downloads, extraction, and AI provider execution until gates exist.

A fifth risk is flattening all domains into one generic search model. Domain packs were introduced precisely to avoid that.

A sixth risk is treating IA metadata as accepted truth. IA observations must become evidence candidates and review items, not direct reviewed records.

A seventh risk is losing the conceptual importance of frontier-resolution media. That discussion expands Eureka’s purpose and should not be discarded as an off-topic aside.

## 13. Larger Project Contribution

This chat contributes a major integration chapter to the Eureka project. It connects recovery, local product architecture, active search/HUNT, first-source IA proof, synthetic evaluation, domain modularity, relation-guided discovery, extraction, and production roadmap.

Its unique value is that it shows the project moving from “avoid scaffolding failure” to “build a general artefact-resolution engine.” It contains both operational prompts and conceptual framing. It likely overlaps with other chats about R0, LOCAL, HUNT, AIDE, SYN, and IA; aggregation should merge those carefully and preserve visible uncertainty.

The chat’s most book-worthy material includes: the critique of scaffold-heavy work; the definition of Search Hunt as a resumable investigation; the universal artefact-resolution engine model; the frontier-resolution media wedge; the progressive IA search lanes; and the rule that synthetic queries create pressure while real sources create evidence and review creates accepted records.

Before merging into a formal spec, all repo-state claims need verification. Many are based on pasted status reports or assistant checks visible in the chat, not a final audited repository state at the date anchor.

## 14. What To Remember

Remember that the user’s core demand was not just more features but proof of real product behavior. Every future task must be tested through the local appliance/HUNT/evidence/review/index path where applicable.

Remember that Eureka’s product identity expanded into a universal artefact-resolution engine. It should resolve hard objects across domains, not just find old software.

Remember that HUNT is the active investigation spine. Misses become Hunts, exhaustion reports, SearchNeeds, and WorkUnits.

Remember that IA is the first real source-family proof, but the desired IA “deep search” must be progressive, budgeted, and evidence/review-gated.

Remember that SYN is not fake data generation. It is evaluation and query pressure.

Remember that DOMAIN packs make the system general, SCOUT makes discovery relation-guided, and F makes hidden-member discovery real.

Remember that source observations are not truth, AI output is not truth, synthetic data is not evidence, and review is required before records become accepted.

Remember that public production is still far away and requires operations, abuse controls, security, privacy, source policy enforcement, backups, rollback, monitoring, and takedown workflows.

## 15. Final Plain-English Summary

This chat captured a long, evolving planning and architecture session for Eureka. The user began from frustration that prior task execution had created too much scaffold and not enough working product. The conversation answered that by defining a stricter product-building doctrine: tasks must produce runtime behavior, persistent state, CLI/API/UI proof, tests, validators, audit evidence, local workbench integration, and no forbidden side effects. This doctrine shaped everything that followed.

The conversation then developed and preserved the architecture of Eureka as a local-first artefact-resolution system. R0 recovered production seams such as source observation, source cache, evidence ledger, review queue, and reviewed index. LOCAL made the system runnable as a local appliance. HUNT turned search into an active, replayable investigation with Hunts, exhaustion reports, SearchNeeds, WorkUnits, deterministic workers, replay, and disabled AI escalation. PLAY was introduced to make the local workbench useful with demo queries and seed objects. IA became the first real source-family proof, with a metadata-only Internet Archive pilot that, according to visible reports in the chat, reached source-cache, evidence, candidate, review, and reviewed local index proof on `dev`.

The chat also widened Eureka’s identity. A discussion of early HDTV / D-Theater / frontier-resolution observational media showed that the project should not be limited to software and drivers. Eureka should resolve any hard artefact whose identity, provenance, representations, source lineage, and best access path are scattered. That led to the idea of a universal artefact-resolution engine with domain packs. Domain packs would allow the same kernel to support legacy software, drivers, frontier media, manuals, scans, packages, source releases, research papers, datasets, books, games, maps, audio, web captures, and other domains without hardcoding all of them into the engine.

The chat repeatedly emphasized safety and truth boundaries. No live source observation should become truth automatically. No AI output should become truth. No synthetic query should create evidence. No downloads, installs, extraction, public deployment, source crawling, or model/provider calls should happen before explicit gates. Review remains the thing that promotes candidates into reviewed records. This is the project’s trust model.

Near the end, the user asked for the ultimate plan and specifically wanted a local HTML page that could search the entire Internet Archive deeply and show results coming through while waiting. The chat refined this into a progressive IA connector architecture rather than a single giant crawl. The page should first search the reviewed local index, then local candidate/source cache, then bounded live IA metadata, then item metadata and file manifests for selected candidates, then evidence candidates and review items, then reviewed index updates. Deeper archive/package extraction must be deferred to F0 gates. This design preserves the user’s desired interactive experience while avoiding unsafe source fanout, downloads, or uncontrolled crawling.

The final visible repo state discussed in the chat was that `dev` was ahead of `main` by 22 commits and included IA/PLAY work. This report does not independently verify that final state. The next operational decision remains whether to promote the IA pilot baseline to `main` before proceeding to SYN, or to continue on `dev`. The assistant recommendation in the visible chat was to run an IA-to-main promotion review if gates pass, then begin SYN. SYN should be treated as a query/eval pressure system over Local/HUNT/PLAY/IA, not just a dataset generator. After SYN, DOMAIN, SCOUT, F extraction, G ranking/explanation, H source expansion, I packs/federation, J actions/preservation, K AI assistance, D snapshots/relay, C native clients, E hosting, and L ecosystem complete the path toward public stable production.

The most important thing for future readers is that this chat is not merely a list of prompts. It is a record of the project’s architectural convergence. Eureka is becoming a local, evidence-first, domain-extensible artefact-resolution engine. The best next action is to verify the current repo state, promote the IA/PLAY/HUNT baseline to `main` if gates pass, and then begin SYN or IA-DEEP planning with the progressive result-lane model.

# Reader Status

- Chat title: Eureka HUNT, IA, SYN, and Artefact Resolution Planning
- Report type: human-readable archive report
- Main value of this chat: It integrates recovery, local appliance, HUNT, PLAY, IA, SYN, DOMAIN, SCOUT, F, and production-roadmap thinking into one coherent artefact-resolution plan.
- Most important decision: Eureka should proceed as a local-first, evidence-first universal artefact-resolution engine, with HUNT as the investigation spine and IA metadata as the first real source-family proof.
- Most important unresolved issue: The exact current repo state and whether IA/PLAY/HUNT work on `dev` has been promoted to `main` must be verified before execution.
- Most important next action: Verify branch/repo state and run IA-to-main promotion review or IA-DEEP planning according to the latest state.
- Safe for aggregation: with caveats
- Main caveats: Several repo-state claims are based on visible status reports and assistant tool checks from the chat, not a final verification performed for this archive report; many roadmap items are proposed, not implemented.
