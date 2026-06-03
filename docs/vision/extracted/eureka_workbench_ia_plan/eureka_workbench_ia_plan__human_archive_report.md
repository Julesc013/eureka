# Human Archive Report — Eureka Workbench, IA Connector, and Production Path

## 1. Orientation

This chat was mainly about keeping the Eureka project coherent while it moved from planning, prompt generation, and control-plane scaffolding toward a real local artefact-resolution engine. The visible conversation spans several stages of the project’s evolution: commit-message discipline, queue and WorkUnit recovery, large-scale roadmap design, repeated Codex prompt generation, live repository state checks, a crisis over scaffold-heavy architecture, recovery planning, later confirmation that the branch had been re-grounded, the emergence of PLAY/HUNT/IA as a usable local workbench path, and finally a discussion about what the Internet Archive connector and Workbench should ultimately become.

The user’s underlying problem was not merely “what is the next prompt?” The user was trying to prevent Eureka from turning into a pile of documents, policies, validators, and generated audit packs that looked impressive but did not behave like software. Across the chat, the user repeatedly pushed for concrete utility: a system where a local HTML page can accept a query, show results from an index, launch or inspect Hunts and WorkUnits, consult real external metadata sources such as Internet Archive, create evidence candidates, route them through review, rebuild a reviewed local index, and eventually become a public hosted product. The pressure driving the conversation was that the project’s scope was large enough to drift into architectural overgeneration. The user wanted a plan that preserved ambition without losing executable reality.

At the start of the visible material, the project was being described through broad tracks: Track 0 for queue and control hardening, Track A for representation and view models, Track B for nodes, needs, WorkUnits, candidates, evidence, review, and packs, then IA, D, C, E, F, G, H, I, J, K, and L. That plan was comprehensive but still abstract. Over time, the chat moved from that grand plan into specific Codex prompts. Many prompts were generated in the required one-line ID-first format, covering extraction, ranking, packs, actions, snapshots, relay, native clients, hosting, MVP audits, operator review, deployment planning, local iteration, source expansion, and recovery. Those prompts are important as an archive of intended work, but the conversation later recognised that prompt generation is not the same as product progress.

A major turning point occurred when the user challenged the live `dev` branch as a “fucking mess,” saying it seemed as if “none of the actual code exists” and the project was “pretending to make a solution.” That was not dismissed. The conversation accepted the criticism and reframed the H-series outputs as mostly Source OS scaffolding: valuable as design inventory, policies, fixtures, candidate schemas, and audit evidence, but not automatically production runtime. The proposed fix was a recovery phase that would classify artifacts, quarantine task-shaped runtime, impose naming and boundary guards, and rebuild clean production seams. This mattered because it prevented a common failure mode in agent-driven software work: task IDs, audit vocabulary, and safety booleans leaking into runtime architecture.

Later visible updates changed the picture again. The user pasted and the assistant discussed a newer live state in which HUNT had been promoted, AIDE golden evals were green, warnings were zero, PLAY was available, and an Internet Archive metadata pilot had completed through a reviewed local index proof. In that later state, the branch was no longer only a scaffold mess. The chat recorded that Eureka had a local appliance/workbench, HUNT, PLAY, and a first real IA metadata vertical slice. This was a different phase: not production, not public-hosted, and not a marketplace, but no longer merely abstract. The project had a real local source-backed discovery loop.

The final direction of the conversation was the Workbench. The user asked whether the Workbench should become the internal superset of the final product rather than a temporary admin page. The answer developed into a central doctrine: one kernel, many projections. The Workbench should exercise the same backend contracts, source machinery, review/index machinery, and result packets that later public web, API, CLI, native, mobile, snapshot, and relay clients consume. The Workbench should be “Eureka Mission Control”: a full local/operator cockpit where search, Hunts, WorkUnits, source probes, source cache, evidence, candidate review, index rebuilds, SYN evaluations, domain packs, Scout graph work, extraction, and ops are made visible and testable. The public app should later be a constrained, safe projection of the same system, not a separate rewrite.

The main outcome of this chat is therefore a staged product doctrine. The project should not jump directly to “connect every source” or “host public search.” It should first make the local Workbench visibly useful, promote the IA metadata pilot baseline, wire IA into live Hunt/result lanes, then run SYN over actual visible behavior, then add DOMAIN and SCOUT, then F extraction, and only then scale sources, packs, actions, AI, snapshots, native clients, hosting, and wider ecosystems. The future relevance is high: this chat is a record of how the project shifted from broad generated architecture to a concrete, source-backed, Workbench-centered path toward stable hosted production.

A future reader should understand the rest of this report as a map of that transition. Some items in the chat were explicit user preferences or decisions, such as prompt IDs first and the desire for a Workbench that is not throwaway. Other items were assistant recommendations that the user did not explicitly accept within the visible transcript. This report preserves that distinction. It also preserves uncertainty: live repository facts changed over time, many claims came from pasted status summaries or visible GitHub connector results, and the exact state after this chat must be reverified before execution.

## 2. The Story of the Conversation

The visible conversation began in the middle of an ongoing Eureka planning and prompt-generation workflow. The user had already been asking for “Next” repeatedly, receiving long Codex prompts for the next tasks in a queue. Early visible material included discussion of commit message standards and task recovery. The user disliked the existing Git commit format and wanted commits to be understandable at a glance while also containing detailed Markdown changelog bodies that could later compile into release notes. A solution emerged around Conventional Commit subjects, structured Markdown bodies, machine-readable trailers, commit linting, changelog preview, and replay-safe WorkUnit recovery. The larger design point was that every future task and commit should be changelog-ready, audit-ready, and resumable.

The discussion then broadened into an “Eureka Converge” plan. The project was reframed around Track 0 for queue/control hardening, Track A for representation and view-model spine, manual observations, Track B for nodes/needs/work-units/candidates/evidence/review, and later tracks for IA, snapshots, native clients, hosting, extraction, ranking, sources, packs, actions, AI, and wider clients. The user insisted that every generated prompt should start with its ID and later refined the header format to include the ID, track, date and time, title, and summary on one line. This became part of the working convention for subsequent prompt generation.

Several turns focused on observation. Initially, the plan included Manual Observation Batch 0, but the user objected that they did not have time to manually find results and instead wanted agents and subagents to do searches, index archives, read forums, discover edge cases, and present candidates for human approval. That shifted the observation lane from manual-only to an agent-assisted, review-gated workflow. The Workbench and source-observation ideas later inherited this principle: agents can discover and propose, but review promotes.

The chat then generated a long series of concrete prompts. These included F-BUNDLE prompts for extraction sandbox and candidate search integration; G-BUNDLE prompts for result explanations and ranking shadow runtime; I-BUNDLE for pack quarantine and contribution review; J0 for safe actions; D-BUNDLE for snapshots and relay; C-BUNDLE for native skeletons, C89 library, WinForms proof, Win32/AppKit/Carbon skeletons, and packaging manifests; E-BUNDLE for hosting readiness and hosted wrapper rehearsal; MVP alpha audits, operator review, deployment planning, and local MVP iteration routing. These prompts are a major artifact of the chat. They show how the plan was operationalized, but later conversation also questioned whether too many generated bundles had become a problem.

The first live repository check visible in this chat concerned `julesc013/eureka/dev`, not `main`. The assistant reported, using the GitHub connector, that `dev` was ahead of `main` and pointed to `H2-BUNDLE-01` after `LOCAL-MVP-ITERATION-01`. The user then pasted a reflection that the older IA/H0/H1 plan had become historical context and that the live queue had advanced to H2 package-registry policy packs. The conclusion at that stage was that the branch was on track but should not merge blindly into `main`. H2 was considered the right next non-deploy source-expansion step, while deployment, J1 risky actions, K semantic/AI, and L wider clients remained deferred.

The conversation then shifted sharply after the user pasted a later analysis saying that after H14 the plan should stop, freeze expansion, and insert a production architecture recovery track. The critique was that H0–H14 had created a lot of Source OS scaffolding—contracts, policy packs, audit packs, fixture contracts, candidate schemas, validators—but not enough production runtime. The project needed to separate control-plane artifacts from domain contracts and real runtime code. The user asked whether these updates were right and said the live code on `dev` was a mess. The answer agreed. Representative files such as H1 and H14 connector normalizers, source-cache helpers, and ranking shadow runtime were described as fixture-only, preview-only, shadow-only, and task-shaped. A recovery phase, R0, was recommended to classify artifacts and block F0 until reality was restored.

Another visible repository update then changed the active state again. The user pasted a later status showing HUNT complete, AIDE evals green, warnings zero, and `SYN-00` recommended. The assistant checked and reported that `dev` and `main` were identical at that moment, and that the repo health file showed HUNT promotion gates passed, source probes and extraction disabled, production/public launch claims false, and SYN ready. The conversation then reworked the plan into a staged capability ramp: PLAY to make the local workbench useful, IA to prove the first real metadata source loop, SYN to pressure-test behavior, DOMAIN to add generality, SCOUT to add discovery intelligence, and F to make hidden-member discovery real.

A still later user status stated that by 2026-05-19 the IA metadata pilot had completed through reviewed local index proof, but `dev` was again ahead of `main` by 22 commits. The live health file, as discussed in the chat, recorded that PLAY was available, IA metadata live probe succeeded with two HTTPS requests, source-cache/evidence/candidate/review/reviewed-index stages passed, and production/public readiness remained false. This established a new “real” milestone: Eureka had moved from architecture and local workbench to local workbench plus HUNT plus demo corpus plus first external metadata source loop.

The user then expressed the desire for a complete Internet Archive end-to-end search connector: a local HTML page where a query searches the entire Internet Archive deeply, starts indexing sources, metadata, files, archives, subdirectories, and packaged files, and streams results to the page. The answer corrected the framing. It agreed with building a complete IA connector, but not as a single synchronous page request that deeply indexes all archive.org while the user waits. The better plan was progressive search: reviewed index results first, candidate and source-cache lanes next, IA metadata jobs next, then item/file metadata expansion, review, and future index rebuilds. The chat proposed an IA workbench plan with result lanes, jobs, polling endpoints, source observation, evidence, review, and deepening frontiers.

The final major turn was the Workbench. The user pasted a synthesis that the Workbench should be the internal superset of the final Eureka product—not a throwaway admin page. The answer agreed and refined it. The Workbench should be “Eureka Mission Control,” not the public app. It should prove every backend feature, frontend pattern, source connector, review flow, eval, audit, and safety boundary before anything becomes public or native. The public app should later be a safe projection of the same packets and kernel. The next recommended path became: promote the IA baseline, build Workbench foundation, add result lanes, add event polling, bridge IA into Hunt and WorkUnits, and then run SYN against the visible system.

The final state of the visible chat is therefore not a single prompt or queue item. It is a product architecture decision: Eureka’s next phase should focus on making the Workbench the canonical proving ground for the source-backed discovery loop, especially IA metadata through HUNT/result lanes, before expanding sources, hosting, marketplace-like actions, AI, or native clients.

## 3. Main Themes

### From Scaffolding to Real Product Behavior

One of the central themes was the distinction between scaffolding and product. Many generated artifacts—contracts, validators, audit packs, fixture schemas, boundary reports, policy matrices—were useful but insufficient. The user became concerned that the project was “pretending” to build a solution. The chat accepted that concern and repeatedly returned to the rule that a task is not complete merely because it added docs, examples, validators, and booleans. A real product capability must have runtime behavior, persistence where relevant, API or packet output, a Workbench or user-facing path, behavior tests, integration tests, and visible operator value.

This theme connects directly to the larger Eureka project because the project is ambitious enough to drown in its own planning artifacts. The chat’s contribution is a corrective: preserve scaffolding as evidence and design material, but do not confuse it with software.

### One Kernel, Many Projections

The final Workbench doctrine is the strongest architectural theme. Eureka should have one kernel that handles search, HUNT, source observation, source cache, evidence ledger, candidate index, review queue, reviewed index, WorkUnits, source policies, evals, audits, and snapshots. Different surfaces—the local Workbench, public web, API, CLI/TUI, native clients, mobile, snapshots, relay—should project the same underlying packets and models with different permissions and visibility. The Workbench is the internal/operator superset; the public app is a restricted safe projection.

This theme emerged late but reorganized earlier ideas. Track A’s view-model spine, Track D snapshots/relay, Track C native clients, and Track E hosting all become less likely to fork semantics if the Workbench proves shared packets first.

### Review Before Truth

The project’s trust model remained consistent throughout. Autonomy may discover; candidates may propose; evidence may support; review may promote; only reviewed evidence-backed records become public truth. This was repeated in various forms across source expansion, IA, SYN, SCOUT, extraction, AI, and public hosting discussions. It is the guardrail against connector results, AI output, forum material, or synthetic data becoming accepted records by accident.

In the IA pilot, this principle became concrete: source observations became source-cache records, evidence candidates, candidate records, review items, promotion previews, reviewed records, and reviewed local index output. The chat treated that as a major breakthrough because it moved the trust model from doctrine to a local vertical slice.

### Internet Archive as the First Real Source Loop

Internet Archive appeared first as one connector among many, then became the first meaningful external source pilot. The user wanted complete IA search and deep indexing. The answer distinguished metadata-only local pilot from full archive.org integration. The IA plan became layered: metadata search, item metadata, file inventory, source cache/evidence/review, demand-driven deepening, and later extraction/member discovery. This matters because IA is both high-value and dangerous if treated as a single broad crawler. The chat settled on progressive, reviewed, demand-driven IA integration.

### PLAY, SYN, DOMAIN, SCOUT, and F as a Capability Ramp

Rather than treating PLAY, IA, SYN, DOMAIN, SCOUT, and F as separate roadmap ideas, the chat synthesized them into a staged ramp. PLAY makes the local workbench useful. IA proves one real source loop. SYN adds evaluation pressure. DOMAIN keeps the engine generic. SCOUT adds relation-guided discovery. F handles hidden-member extraction. This is a major planning contribution because it prevents the project from jumping directly from local workbench to every connector or from SYN to abstract synthetic data without product anchors.

### Public Production Is Far Away and Must Stay Honest

The chat repeatedly rejected premature public hosting, public live fanout, downloads, uploads, accounts, telemetry, marketplace/app-manager behavior, native app-store ambitions, and production claims. Public alpha can eventually search reviewed records with clear non-claims, but production requires rate limits, observability, backups, rollback, incident response, privacy, takedown workflows, source terms compliance, security review, stable APIs, and operational ownership. This theme keeps ambition grounded.

## 4. What We Were Actually Trying To Achieve

Explicitly, the user wanted plans, prompts, and repository-state interpretation for the Eureka project. The user asked for next prompts, live branch checks, a better source/connector plan, a complete Internet Archive connector plan, and ultimately a Workbench-centered product architecture. The user also wanted a complete list of what is needed to reach public stable hosted production.

Inferred from the visible chat, the deeper goal was to force the project to become a real local, source-backed artefact-resolution engine rather than an agent-generated archive of policies and prompts. The user wanted the system to be useful locally before public hosting: a local HTML page, an operator Workbench, real Hunts and WorkUnits, external source observations, reviewable evidence candidates, reviewed index rebuilds, and progressive search results.

The goals changed several times. Early on, the active work was prompt generation for planned tracks. Then it became dev branch validation and deciding whether to continue H2 or recover architecture. Later, once HUNT/PLAY/IA were described as complete on dev, the goal shifted from recovery to product sequencing: how to make the workbench useful and how to build the IA connector end-to-end. The final goal was neither “recover from a mess” nor “connect everything”; it was to make the Workbench the canonical proving ground and wire IA into visible Hunt/result lanes.

The unresolved goals are large. Eureka still needs Workbench foundation, IA-HUNT integration, SYN foundry, DOMAIN packs, SCOUT, extraction, ranking/explanation, broader source expansion, packs/federation, safe actions, snapshots/relay, native clients, hosting, and production operations. The chat does not establish that those are built; it establishes a proposed sequence and rationale.

## 5. Decisions and Commitments

### Structured commit and WorkUnit discipline

A visible early decision was that Eureka/AIDE work should use Conventional Commit-style subjects, structured Markdown bodies, changelog categories, machine-readable trailers, commit linting, changelog preview, and replay-safe WorkUnit recovery. The decision was proposed as a best practice and appears to have been accepted in spirit because subsequent prompts included structured commit requirements. It was motivated by auditability, changelog generation, future agent recovery, and the need to avoid stopping on repeated or out-of-order prompts. This decision could be revisited if the format becomes too heavy, but the underlying goals—glanceable history, changelog-ready commits, resumable tasks—remain sound.

### Prompt IDs and header format

The user explicitly required that generated prompts begin with the prompt ID so queue order can be identified. Later the user specified a one-line header format: `X-N (Track) — YYYY-MM-DD HH:MM:SS TZ — Title — Summary`. This was accepted operationally, and many generated prompts followed it. This is a settled style preference for prompt-generation work. It matters because the project uses long multi-step queues; losing prompt identity causes confusion.

### Manual observation should become agent-assisted review

The user rejected the assumption that they would manually perform large search observation batches. The accepted direction was that agents should generate candidate observations, edge cases, source leads, and search failures for human approval or rejection. This decision is important but still partly conceptual. It should not be interpreted as permission for uncontrolled scraping or unreviewed evidence creation.

### H-series scaffolding is useful but not production

A major decision was to stop treating large H-series source expansion outputs as production implementation. The plan to insert R0 production reality recovery was accepted in context when the dev branch appeared over-generated and runtime was task-shaped. Later repository state changed, but the principle remains: task-shaped runtime, fixture-only modules, preview-only outputs, and audit schemas must not be counted as production capabilities. This decision remains valid as a guardrail even if the live branch later improved.

### PLAY, IA, SYN, DOMAIN, SCOUT, F as a staged ramp

The chat adopted a staged capability ramp: PLAY, IA, SYN, DOMAIN, SCOUT, F. This was a planning synthesis rather than an executed decision. It makes sense because SYN is more useful after real local anchors, DOMAIN prevents hardcoding, SCOUT depends on domain relations, and F extraction benefits from query pressure and source relations. It could be revisited if IA-HUNT integration reveals a different bottleneck, but it is currently the clearest strategic sequence.

### IA should be progressive, reviewed, and local-first

The user wanted a complete IA end-to-end connector. The accepted framing was that IA should be built end-to-end, but not as a synchronous “search all archive.org deeply while waiting” request. The chosen design is progressive: reviewed index first, candidate/source-cache lanes next, IA metadata jobs, item/file metadata expansion, review, local index rebuild, and later demand-driven deepening and extraction. This decision is central and should be preserved.

### Workbench as internal superset

The final and most important decision in the chat was that the Workbench should be the internal/operator superset of the final product. It should not be a temporary admin UI or a separate implementation. It should prove the kernel, packets, result lanes, Hunts, WorkUnits, sources, evidence, review, index rebuilds, evals, and safety boundaries. Public web and native clients should later be projections of the same system. This was strongly endorsed in the assistant’s response to the user’s synthesis, but the visible chat ends with the assistant recommendation rather than an explicit user “accepted.” It is therefore best treated as a strong proposed doctrine, likely aligned with user intent, but still subject to implementation confirmation.

## 6. Rejected, Superseded, or Deprioritised Ideas

The chat repeatedly rejected going straight to broad connector expansion. The reason was that adding every site, source, mirror, forum, package registry, and archive before the Workbench and IA loop are visible would recreate the scaffolding failure. Source policies and disabled definitions can be collected, but live connector runtime should expand only after one source loop is proven in the Workbench.

It rejected “full Internet Archive integration” as a first step. The first step is IA metadata-only local pilot and then progressive workbench search. Downloads, collection crawling, Wayback replay, S3/write APIs, public fanout, arbitrary URL fetches, and deep file extraction are explicitly later.

It rejected direct F0/extraction continuation at one point when the branch state looked scaffold-heavy. Later, after IA/PLAY/HUNT improvements, F returned as a later phase after SYN, DOMAIN, and SCOUT. Thus F is not permanently rejected; it is deferred until the system can generate useful extraction WorkUnits and reviewable member observations.

It rejected early marketplace or app-manager ambitions. Those require download, mirror, install, execute, rights, malware, quarantine, trust, rollback, and moderation systems that are not built. Marketplace remains a distant descendant of the Workbench and action layers, not a near-term goal.

It rejected public hosted production as near-term. Hosted public alpha is later and must start as a constrained reviewed-index search with honest non-claims. Stable hosted production is much later and requires serious operations, security, privacy, backups, incident response, takedown, source terms, and monitoring.

It also rejected the notion that the public app should be a separate implementation. The preferred model is projection from the same kernel and packets.

## 7. Rationale, Tradeoffs, and Design Logic

The visible design logic is a balance between ambition and safety. Eureka’s ambition is broad: universal artefact resolution across software, drivers, media, documents, packages, archives, source hosts, IA, Wayback, future AI, snapshots, native clients, and public hosting. The risk is that such breadth causes endless generation of policies and schemas. The tradeoff chosen is depth before breadth: one real IA source loop, one Workbench path, one reviewed local index flow, then SYN pressure, then domain and source expansion.

Another tradeoff is synchronous UX versus progressive background jobs. The user wanted search results to come through to the page while indexing proceeds. The answer agreed but avoided a blocking “search all IA deeply” model. Progressive lanes and polling jobs preserve responsiveness and source-policy control. They also allow review before truth and support future rate limiting.

The Workbench itself is a tradeoff. Building an overpowered internal Workbench takes effort, but it prevents backend work from remaining invisible. It also keeps public product development safer because public pages become projections of tested packets rather than separate semantics. The second-order benefit is that future source connectors, extraction tools, SYN evals, and review flows must prove themselves in one cockpit.

The user cares about not losing context, not repeating rejected work, and not being fooled by superficial progress. They also care about big-picture completeness: stable hosted production, app/native future, broad sources, and a “whole internet archive” style ambition. The plan tries to preserve that ambition while imposing review gates.

If the context is misunderstood, future assistants might restart old prompt-generation queues, treat H-series artifacts as completed production, merge dev into main without review, implement broad scraping, enable IA fanout, create fake synthetic evidence, or build public UI disconnected from the Workbench. Those are the main things this report should prevent.

## 8. Current State at the End of This Chat

At the end of the visible chat, the latest discussed repository state is dated 2026-05-19 in the pasted/verified health material, while this archive uses 2026-05-31 as the date anchor requested by the user. The live state should be treated as possibly stale after that date unless rechecked.

Within the visible chat, the final known state is:

- `dev` was reported as 22 commits ahead of `main` and 0 behind at the IA/PLAY stage.
- HUNT was complete.
- PLAY was available, including known hit, known absence, operator session, and smoke pack.
- IA metadata policy was approved.
- IA fixture replay was hardened.
- IA live metadata probe had succeeded with two HTTP requests.
- IA source-cache, evidence, candidate, review queue, promotion dry-run, reviewed local index rebuild, search/object/absence proof, and closeout had passed.
- The full IA metadata vertical slice was recorded as complete.
- Full archive.org integration was not claimed.
- Production readiness and public launch readiness were not claimed.
- Public fanout, provider calls, extraction execution, and deployment remained disabled.
- The current recommended task in the health report was `SYN-00 — Synthetic Query Foundry planning over Local/HUNT/PLAY/IA`, but the final recommendation in the conversation was to insert Workbench foundation before running SYN in earnest.

The settled conceptual state is that the Workbench should become the internal superset/proving surface. The tentative operational next sequence is IA promotion to main, then Workbench Foundation, result lanes, events, IA-HUNT bridge, IA WorkUnit and UI steps, apply gate, then SYN.

The main unresolved issue is whether the user wants to promote the IA baseline from `dev` to `main` before Workbench work, or continue on `dev`. The assistant recommended promotion first, but this is not confirmed as executed in the visible transcript.

## 9. Future Work and Next Steps

### IA-to-main promotion

This should happen first if the IA pilot baseline is ready and the user wants main to become canonical. It matters because SYN and Workbench work should start from a stable source-backed baseline. It depends on promotion gates passing and no forbidden boundaries being crossed. Its output should be a main branch containing HUNT, PLAY, and IA pilot closeout. Failure modes include merging too early, losing control-plane evidence, or promoting dev-only assumptions.

### Workbench Foundation

This should define the Workbench doctrine, route matrix, shared packets, permission model, public projection model, unsafe-action visibility rules, and smoke requirements. It matters because the Workbench is the bridge between backend proof and product behavior. It should avoid implementing a huge UI at once. Output should include route/view/API matrices for search, hunts, needs, WorkUnits, sources, candidates, evidence, review, index, SYN, domain, scout, extraction, and ops.

### Workbench Result Lanes

This should make the local search page show reviewed results, candidates, source-cache hits, IA metadata candidates, review queue items, known absence, blocked actions, and running WorkUnits. It matters because this is the first user-visible version of the progressive search model. The main risk is mixing unreviewed candidates with reviewed truth without clear labels.

### Workbench Event Model

This should implement polling-first job/event endpoints for Hunt and search progress. It matters because IA metadata and later extraction/source work should appear progressively without blocking the page. The risk is overengineering WebSockets too early; polling is enough.

### IA-HUNT Bridge

This should wire IA metadata into the Hunt/WorkUnit flow so query misses can generate SearchNeeds, IA WorkUnits, source observations, evidence candidates, review items, and reviewed-index updates. This is the next “real product” milestone. The risk is skipping review or writing directly to public/accepted indexes.

### SYN over Workbench-visible behavior

SYN should generate pressure against known local hit, absence, IA candidate, reviewed IA-backed hit, near miss, blocked download, blocked extraction, blocked AI, latency, queue, review, and index rebuild cases. It should not create fake evidence or fake verified records.

### DOMAIN, SCOUT, and F

DOMAIN should define domain packs for legacy software, drivers, frontier media, manuals/docs/scans, and packages/source releases. SCOUT should add relation-guided discovery over domain relations and source trust. F should add safe extraction/member discovery after the system can generate useful extraction WorkUnits. These phases matter for making Eureka general rather than a one-source IA demo.

### Production roadmap

Longer-term work includes search quality/ranking/identity, broader sources, packs/federation, safe actions, snapshots/relay, native clients, hosted public alpha, public beta, and stable hosted production. Each requires separate gates and should not be collapsed into the IA/Workbench phase.

## 10. Artifacts, Files, Prompts, and Outputs

This chat discussed or generated many artifacts, most of them as prompt text rather than actual files. The major generated prompt families were:

- Extraction prompts: F-BUNDLE-01 and F-BUNDLE-02 for extraction sandbox, Tier 0–2 fixtures, candidate effects, and search integration.
- Search quality prompts: G-BUNDLE-01 and G-BUNDLE-02 for explanations, near misses, known absence, ranking shadow runtime, and search-quality harness.
- Pack and action prompts: I-BUNDLE-01 for pack quarantine and J0-BUNDLE-01 for safe action manifests.
- Snapshot/relay prompts: D-BUNDLE-01 and D-BUNDLE-02 for snapshots, verification, renderers, localhost read-only relay, old-browser and terminal modes.
- Native prompts: C-BUNDLE-01, C-BUNDLE-02, C-BUNDLE-03 for native skeleton, matrix, C89 library, WinForms, Win32, AppKit, Carbon, smoke evidence, and packaging manifests.
- Hosting and MVP prompts: E-BUNDLE-01, E-BUNDLE-02, MVP-ALPHA-AUDIT-01, MVP-ALPHA-OPERATOR-REVIEW-01, PUBLIC-ALPHA-DEPLOYMENT-PLAN-01, and LOCAL-MVP-ITERATION-01.
- Recovery prompts: R0-LITE-01 and R0-01 concepts for production reality audit and expansion freeze.
- Source expansion prompts: H2 and related plans, later superseded by recovery and then by PLAY/IA/SYN/Workbench staging.
- Workbench and IA plans: not fully converted into formal long Codex prompts in the final visible turn, but strongly articulated as next queue items.

The chat also discussed live repository artifacts, including `.aide/reports/eureka-repo-health.json`, `.aide/context/latest-task-packet.md`, `.aide/queue/SYN-00/task.yaml`, IA audit directories, PLAY audit directories, HUNT promotion artifacts, and many `control/audits/**` and `control/inventory/**` files. These artifacts were not created by this archive task; they were referenced as part of the visible conversation.

The most important substance to preserve is not the file list itself. It is the evolution of meaning: the project moved from track plans and prompt generation, through a warning about scaffold-heavy code, to a source-backed IA pilot and a Workbench-centered product doctrine.

## 11. Open Questions and Unresolved Issues

The first open question is whether the IA pilot baseline has been promoted from `dev` to `main`. The visible chat says `dev` was ahead by 22 commits at the later IA stage and recommends IA-TO-MAIN-PROMOTION-REVIEW. It does not show that this was completed. This matters because future work should know whether `main` or `dev` is canonical.

The second question is whether Workbench Foundation has actually been queued or implemented. The final recommendation was clear, but the visible chat ends before execution. A future assistant should not assume Workbench routes, packets, lanes, or event endpoints exist.

The third question is the exact state of the local runtime after 2026-05-19. The archive date anchor is 2026-05-31, but repository facts should be reverified before action.

The fourth question is how much of the IA vertical slice is permanent runtime versus temp-instance/audit proof. The health file as discussed says IA writes were temp explicit instance only and that accepted truth was not automatically created. The next work must determine what is productionized versus proof.

The fifth question is how to sequence SYN relative to Workbench. The repo health recommended SYN, but the final conversation recommended Workbench first so SYN tests visible product behavior. This is a planning choice for the user or project lead.

The sixth question is how public/private roles will be implemented. The Workbench doctrine calls for operator, public, native, and possibly API modes over shared packets, but the permission system remains future work.

## 12. Risks and Failure Modes

The largest risk is over-compression. A future assistant might reduce the chat to “next task is SYN-00” or “next task is Workbench Foundation” and lose the rationale. The important context is that SYN is recommended by repo health, but Workbench is recommended by product sequencing.

Another risk is treating assistant recommendations as user decisions. The Workbench doctrine strongly fits the user’s language, but the final visible response is still an assistant assessment. Future work should treat it as the current best recommendation unless the user explicitly confirms.

A third risk is treating the IA pilot as full IA integration. The chat explicitly rejected that. The IA pilot is metadata-only and local/controlled. Full archive.org search, file downloads, collection crawling, Wayback replay, public fanout, deep indexing, package extraction, and arbitrary source fetching remain future work.

A fourth risk is repeating old rejected plans. The project should not restart H2-H14 broad source expansion, jump to F extraction, build marketplace/app-manager behavior, or host public search before the Workbench and IA-HUNT loop are visible and tested.

A fifth risk is confusing candidate lanes with reviewed truth. The Workbench must label reviewed results, candidates, source-cache hits, IA metadata candidates, evidence candidates, review items, and absence clearly.

A sixth risk is relying on stale branch state. The repository changed several times during the chat. Any future task should verify `dev`, `main`, and the current health report before acting.

## 13. Larger Project Contribution

This chat contributes a high-value strategic synthesis to the Eureka project. It records the project’s transition from generated architecture to a local workbench with a real IA metadata source loop and then to a Workbench-centered product doctrine. It also preserves the caution that scaffolding is not product and that review before truth must govern every source, AI, extraction, and public surface.

It overlaps with other chats likely to contain the actual Codex outputs, repository audit packs, HUNT closeout, IA pilot implementation details, PLAY scripts, and SYN queue work. It may conflict with older chats that identify H2, F0, or SYN as immediate next tasks without the later Workbench correction. The merge handling should treat this chat as a late-stage planning synthesis, not a replacement for actual repository evidence.

Material that could become formal requirements after review includes:
- Workbench as internal superset;
- shared packet families;
- result lanes;
- event polling model;
- IA-HUNT bridge;
- progressive IA search;
- no synchronous deep IA crawl;
- public app as restricted projection;
- SYN over Workbench-visible behavior.

Material that should remain background context includes the large set of generated bundle prompts, except where they still map to future work.

## 14. What To Remember

Remember that this chat is about preventing Eureka from becoming an impressive but hollow scaffold. The user wanted a real local system, not just policies and prompts.

Remember that the final product doctrine is one kernel and many projections. The Workbench is the internal superset; public web and native clients are restricted projections over the same contracts and packets.

Remember that IA should be built end-to-end, but progressively: local reviewed results first, IA metadata candidates next, review and index rebuild later, and deep file/member indexing only after F gates.

Remember that SYN should pressure-test real Workbench-visible behavior, not abstract query files against an empty or hidden backend.

Remember that public production remains far away. No public live fanout, downloads, uploads, accounts, telemetry, marketplace behavior, or production claims should be inferred from the IA pilot.

Remember that the likely best next operational sequence is IA promotion, Workbench Foundation, result lanes, events, IA-HUNT bridge, then SYN.

## 15. Final Plain-English Summary

This chat was a long planning and correction session for Eureka, a project intended to become a local and eventually hosted artefact-resolution engine. The early visible material was dominated by queue management and prompt generation. The user wanted every prompt to be clearly identifiable, every commit to be changelog-ready, every WorkUnit to be resumable, and every future task to preserve context without asking the user to re-drive the system manually. This created a strong control-plane foundation: prompt IDs, structured commit bodies, queue state, validation commands, and auditable handoff packets.

The project then expanded into a comprehensive architecture: representation/view-model spine, manual or agent-assisted observation, node/need/WorkUnit/candidate/evidence/review loops, IA, snapshots, native clients, hosting, extraction, ranking, source expansion, packs, actions, AI, and wider clients. Many Codex prompts were generated for this architecture. That was useful, but it also created the very risk the user was afraid of: lots of contracts, validators, examples, policies, and audit packs that might not equal product behavior.

A major middle section of the chat confronted that risk directly. The user said the dev branch looked like a mess and that it felt as if none of the actual code existed. The answer did not paper over that. It identified the H-series outputs as mostly Source OS scaffolding and proposed a recovery phase to classify artifacts, quarantine task-shaped runtime, separate control-plane from product code, and rebuild clean production seams. This was an important correction because it established a durable rule: generated artifacts support product work, but they are not product work by themselves.

The branch state then appeared to improve. Later visible updates reported that HUNT had been promoted, AIDE evals were green, warnings were zero, PLAY was available, and the Internet Archive metadata pilot had completed through a reviewed local index proof. This changed the discussion. Eureka was no longer only architecture and scaffolding; it had a local workbench, HUNT, PLAY/demo material, and a first external metadata source loop. The IA path included metadata policy, fixture replay, live metadata probe, source-cache path, evidence candidates, provisional candidates, review queue, promotion dry-run, reviewed local index rebuild, and search/object/absence proof. That was treated as the first real source-backed discovery loop.

The user then wanted the next step: a complete Internet Archive end-to-end connector where a local HTML page could accept a query and have the engine search and index IA deeply while results arrive. The answer agreed with the ambition but corrected the mechanism. The right design is not to synchronously search all of Internet Archive deeply while the user waits. The right design is progressive: show reviewed local index results immediately, show candidate/source-cache lanes, start IA metadata jobs, show item/file metadata candidates, create evidence candidates and review items, then promote reviewed records into the local index so future searches return instantly. Deep file/member discovery should come later through extraction WorkUnits and policy gates.

The final synthesis was the Workbench. The user proposed that the Workbench should be the internal superset of the final product, not a throwaway admin dashboard. The answer agreed and developed the doctrine: one kernel, many projections. The Workbench should become Eureka Mission Control: search console, Hunt console, source lab, evidence studio, candidate review, index builder, SYN foundry, domain pack editor, Scout graph, extraction lab, and ops console. The public web product should later be a constrained projection of the same packets and backend, not a separate implementation. Native and mobile clients should also consume the same contracts, snapshots, relay, or API projections.

The best next action at the end of this chat is not more connectors, not public hosting, and not marketplace features. It is to promote the IA baseline if still on `dev`, then build Workbench Foundation: doctrine, route/view/API matrix, shared packet policy, result lanes, polling event model, and IA-HUNT bridge. Once the Workbench exposes the real source-backed loop, SYN becomes valuable because it can test visible behavior: known hits, known absence, IA candidates, review promotion, index rebuilds, blocked download/extraction/AI paths, latency, and event ordering. After that, DOMAIN, SCOUT, and F can add generality, discovery intelligence, and hidden-member extraction.

What must not be forgotten is the reason for the Workbench pivot. Eureka needs to become usable and inspectable before it becomes broad or public. The project should not repeat the old failure mode of adding more source-family policies and audit packs without operator-visible behavior. Every future backend feature should prove itself through runtime behavior, API packets, Workbench views, CLI or smoke tests, behavior/integration tests, and clear blocked-action proof.

# Reader Status

- Chat title: Eureka Workbench, IA Connector, and Production Path
- Report type: human-readable archive report
- Main value of this chat: It records the transition from scaffold-heavy planning to a Workbench-centered, source-backed product path.
- Most important decision: The Workbench should be the internal/operator superset and canonical proving surface for the final Eureka product.
- Most important unresolved issue: Whether the IA pilot baseline has been promoted from `dev` to `main`, and whether Workbench Foundation has actually been queued or implemented.
- Most important next action: Verify current repo state, then run IA-TO-MAIN-PROMOTION-REVIEW if needed, followed by WORKBENCH-FOUNDATION-00.
- Safe for aggregation: with caveats
- Main caveats: Repository state changed several times; many details are based on visible pasted or connector-reported state; assistant recommendations should not be treated as user decisions unless later confirmed.
