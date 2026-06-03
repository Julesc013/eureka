# Human Archive Report — Eureka Codex Prompt Plan and Production Roadmap

Date anchor: 2026-05-31 Australia/Melbourne

Scope note: This report uses only the visible contents of this chat. Some earlier parts of the conversation are represented in the visible transcript only through summaries, pasted synthesis text, and repeated generated prompts. Where the live repository state is discussed, it is treated as a chat claim unless the transcript itself contains a direct execution result. No web or repository verification was performed for this archive package.

## 1. Orientation

This chat was mainly about turning the Eureka project from a broad idea and prototype into a disciplined, queueable implementation roadmap for Codex agents. The visible conversation sits deep inside an ongoing project called the Eureka Archive System. By the time this archive begins, the user and assistant had already generated many Codex prompts, and the visible record shows the continuation and consolidation of that process from the post-P49/P50 audit era through a large sequence of implementation, contract, planning, and dry-run runtime prompts. The user’s aim was not simply to brainstorm features. The user wanted a production-oriented plan that could be handed to powerful autonomous coding agents and executed in a real repository without constant human clarification. The repeated word “Next” drove the assistant to generate prompt after prompt, each intended as one queueable Codex task that would move the repository closer to a live production state while preserving strict safety, evidence, validation, and audit boundaries.

The central problem was how to grow Eureka without turning it into an unsafe crawler, an unverifiable AI wrapper, an app store with false safety claims, or an ungoverned mutation engine. The project’s intended purpose, as established in the chat, is an evidence-first temporal object resolver for archived and current digital objects. In practical terms, Eureka is meant to help a user resolve vague archive/software requests into evidence-backed records: what the object is, where it came from, which version or representation it may be, what compatibility evidence exists, what conflicts or gaps remain, and what safe action is available. The chat therefore focused on building layers: public search contracts, query-intelligence contracts, source cache and evidence ledger contracts, connector approval packs, object/source/comparison page contracts, identity resolution, merge/deduplication, ranking, deep extraction, pack import, and eventually local dry-run runtimes. Each layer had to be introduced in a way that Codex could implement without accidentally crossing into live source calls, downloads, installs, account systems, telemetry, public mutation, or production claims.

The pressure behind the conversation was the user’s desire to queue many prompts “all at once” using GPT-5.5 at high reasoning with subagents, full access, Codex, Git, and AIDE. The user corrected the earlier blocker-handling posture: blockers should exist to catch mistakes, but the agent should not stop and ask the user for input when it finds normal blockers. Instead, each prompt should give enough rationale and fallback guidance for a clean-room coding agent to resolve bounded blockers autonomously. This correction became a defining feature of the subsequent prompts. They repeatedly instructed Codex to inspect blockers, classify them, repair bounded drift, preserve gates, and continue without violating explicit constraints. The prompts also emphasized frequent commits, verbose descriptions, and complete verification.

The main outcome of the visible chat was the generation and synthesis of a long-range prompt queue. The user stated near the end that prompts had been generated up to P107, while the live repository was still around P95. The assistant then explained what had been designed so far, how many prompts remained, and what the broader plan should be. In this final archive request, the user asked for a human-readable report that preserves not only the task list but the meaning of the conversation: what mattered, what changed, what was decided, what remains unresolved, and how the material should feed into a future larger project book. The future relevance is significant. This chat is a record of how the project’s doctrine became operational: “fast learning, slow truth,” “dry-run before runtime,” “review before mutation,” and “public search before live connectors.” It also records the transition point where the assistant advised that continuing to generate unlimited prompts would be less valuable than executing the generated queue, consolidating, and moving toward a minimal live public alpha.

A future reader should understand the rest of this report as a briefing about a planning and prompt-generation session, not as proof that every named milestone was implemented in the repository. The transcript contains many detailed Codex prompts that prescribe what future agents should do. Those prompts are artifacts of intent and design, not automatically factual evidence of repository state. Where the user reported that P50 was complete and later that the live repo was around P95, this report treats those as chat facts attributed to the user. Where the assistant described future prompt ranges, counts, and phases, those are plans or inferences rather than completed work. The enduring value of the chat is the architecture and sequencing logic: Eureka should become live by proceeding from contracts to local dry-runs to authoritative local stores to hosted alpha, while carefully delaying live connectors, public contribution, AI runtime, downloads, installs, and master-index mutation until the appropriate gates exist.

## 2. The Story of the Conversation

The visible portion of the conversation begins after substantial prior work. The user first asks to “put it all together” and to check the live repository state for Eureka, then create the best possible plan for queueable Codex prompts that would implement and document everything properly. The user stresses that this is “the real deal,” not a trial run. That framing set a high bar: each prompt needed to move the repository closer to live production state, not merely add speculative documents.

The assistant generated the first prompt and continued with a sequence. The user then added an important correction. The user said blockers should not cause Codex to stop and ask for input; blockers exist to catch mistakes, but the agent should have enough context to resolve them autonomously. This became one of the conversation’s most important design changes. Every later prompt was written as if Codex were a clean-room developer that could not ask the user for more information. The prompts therefore included rationale, fallback paths, prohibited actions, verification commands, commit plans, and final response requirements.

The user then repeatedly said “Next,” and the assistant generated a long run of prompts. The visible transcript captures the later part of that chain starting with P79 and continuing through P107. The prompt sequence itself reveals the architectural evolution. P79 defined object page contracts. P80 defined source page contracts. P81 defined comparison page contracts. P82 handled cross-source identity resolution. P83 addressed result merge and deduplication. P84 and P85 designed evidence-weighted and compatibility-aware ranking. P86 switched from contract design to runtime planning for public query observations, emphasizing privacy and poisoning guards. P87 through P92 planned runtime paths for first-wave metadata connectors: Internet Archive, Wayback/CDX/Memento, GitHub Releases, PyPI, npm, and Software Heritage. P93 planned object/source/comparison page runtime. P94 planned pack import runtime. P95 defined the deep extraction contract. P96 through P107, generated later, covered search result explanation, ranking planning, source cache/evidence ledger dry-run runtimes, integration audits, connector audits, manual observation follow-up, page dry-run runtime, pack import dry-run runtime, deep extraction runtime planning, explanation runtime planning, and ranking dry-run runtime.

In the middle of the visible chat, the user pasted a large synthesis called “Eureka mega synthesis for P50 and beyond.” This pasted synthesis summarized the state after P49 and framed P50 as a full post-search-and-pack platform audit. It established that Eureka was still a Python reference backend prototype, not a production hosted search engine; that `site/dist` was the static deployment artifact; that GitHub Pages could not run a Python backend; that local public search existed only as a prototype; and that pack contracts, AI contracts, staging contracts, and validation-only tooling had been built or planned. The synthesis also laid out a major roadmap from P50 onward: remediation, static deployment evidence, hosted search, query intelligence, AI-compatible escalation, source sync and live connectors, ranking, object pages, pack import, deep extraction, action/preservation features, semantic/AI runtime, and clients/offline support. This synthesis became a central source for later prompt design.

The user then asked what the “ultimate synthesis” was for achieving a live deployed site and moving beyond it. The assistant responded with a staged path: stop treating GitHub Pages as the backend, use it or another static host as the static surface, add a separate hosted backend, keep live probes disabled for the first public alpha, then add query intelligence and source caches before connectors. The user then asked to generate P50. After P50 was executed, the user pasted a completion summary showing commits, verification results, classifications, top blockers, and the next recommended branch. This P50 summary is important because it grounded the subsequent plan in an audit pack rather than speculation.

After P50, the user again moved the queue forward by repeatedly saying “Next.” The assistant generated a large number of prompts. The prompts became increasingly systematic. Each one opened with a clean-room developer instruction, a primary goal, strict prohibitions, blocker-handling policy, context from previous prompts, core doctrine, deliverables, required files, tests, command matrix, commit plan, and final response requirements. The prompts were intentionally verbose because the user wanted Codex to reason through blockers without stopping.

The final visible planning discussion occurred when the user paused after P107 and asked what had been done, how many prompts remained, and what the full plan was. The assistant answered that prompts had been generated through P107, while treating the user’s statement that the live repo was around P95 as the working fact. The assistant explained that the project had mostly finished designing the safety-gated architecture and now needed to stop expanding indefinitely and convert safe dry-run/planning layers into a minimal live product path. The assistant broke the plan into phases: finish P96–P107, move through authoritative local stores and alpha hardening, launch public alpha, complete manual baselines, build authoritative source/evidence systems, approve the first live connector path, add object/source/comparison pages, add explanation/ranking, introduce pack import, handle deep extraction, expand connectors, and eventually build app-store-style clients and offline ecosystems.

The conversation landed at a strategic checkpoint. The generated prompt queue exists through P107; the live repo is asserted by the user to be around P95; the next best move is to execute P96–P107, then generate and execute only a bounded next tranche around P108–P115 rather than continuing indefinitely. The chat has therefore moved from open-ended roadmap generation into a planned execution discipline.

## 3. Main Themes

### Evidence-first architecture rather than answer-first search

The dominant theme was that Eureka should be an evidence-first resolver, not a simple search box or AI answer layer. This came up because the target domain—archived software, old digital objects, packages, captures, source releases, scanned material, and compatibility evidence—is high-risk for false certainty. A result might be a near match, a wrong version, an unsafe executable, a dead mirror, a source record without payload, a private or rights-restricted item, or a nested member inside a container. The prompts therefore required explicit evidence, provenance, source posture, confidence-not-truth language, rights/risk caveats, and visible gaps. This theme connects to the larger project because it is the difference between Eureka as a useful archive resolver and Eureka as a brittle or misleading search frontend.

### Dry-run before runtime, runtime before public exposure

Another major theme was staged implementation. The user wanted real progress, but the plan consistently avoided jumping directly from contracts to public runtime. The intermediate layer was local dry-run runtimes: source cache dry-run, evidence ledger dry-run, page dry-run, pack import dry-run, and ranking dry-run. These systems prove that records can be loaded, classified, validated, rendered, and reported deterministically without mutating authoritative state. This matters because it allows Codex to write useful code while still preventing dangerous behavior such as live source calls, index mutation, uploads, downloads, and hidden ranking.

### Public search must remain bounded

Public search was repeatedly protected. It should remain local-index-only until explicit later approval. It must not fan out live to Internet Archive, Wayback, GitHub, PyPI, npm, Software Heritage, or any arbitrary URL. It must not read dry-run runtimes as authoritative stores, mutate source/evidence/candidate/master records, or expose unapproved routes. This theme developed because the project’s public site is the first real user-facing surface. If public search is unsafe, every later subsystem becomes risky. The prompts therefore include multiple audits and boundaries to ensure that dry-run and planning systems do not accidentally become public runtime.

### Connector approval before connector runtime

The connector sequence was deliberately split into approval packs, runtime planning packs, audits, and only later possible live probes. This came up because every source has different policy and safety constraints. Wayback involves URI privacy and arbitrary URL risk. GitHub involves private repository and token boundaries. PyPI and npm involve package installation and dependency-resolution hazards. Software Heritage involves source-code content and repository identity. The plan rejected the temptation to add “all APIs at once.” Instead, connectors must go through source policy review, User-Agent/contact decisions, rate limits, circuit breakers, cache-first outputs, evidence-ledger candidates, and review.

### Page, identity, merge, ranking, and explanation as resolver features

The chat defined a cluster of features that make Eureka a resolver product rather than a result list. Object pages explain things. Source pages explain source coverage and posture. Comparison pages explain differences and conflicts. Identity resolution says whether records might refer to the same thing. Merge/deduplication groups results without destructive merging. Ranking uses evidence and compatibility factors, but cannot become truth. Explanations tell users why a result appeared. This theme matters because it is the user-facing intelligence layer of Eureka.

### Human/operator work remains necessary

The plan repeatedly preserved human/operator gates. Manual Observation Batch 0 must be executed by a human. Source/API policies must be reviewed by a human. User-Agent/contact values must be decided by an operator. Hosted deployment must be verified. Authoritative source/evidence storage needs policy decisions. This matters because Codex can write and validate code, but it should not fabricate external observations, source-policy approval, deployment evidence, or legal/safety determinations.

## 4. What We Were Actually Trying To Achieve

The explicit user goal was to create a series of queueable Codex prompts that would implement and document Eureka “properly” and move it toward live production state. The user wanted the prompts to maximize Codex, Git, and AIDE, with frequent detailed commits and enough rationale that a clean-room coding agent could autonomously resolve blockers. The user also wanted to understand the current state after many prompts and eventually to archive the conversation as source material for a larger project book.

An inferred goal was to prevent the project from drifting into either over-planning or unsafe implementation. The user repeatedly drove the prompt sequence forward, but also accepted and requested strategic discussion at major checkpoints. The assistant’s later recommendation—execute P96–P107, then consolidate before generating unlimited new prompts—reflects this inferred goal: the project needs momentum, but not uncontrolled prompt sprawl.

The goals changed over time. Early visible discussion focused on P50 as a major audit after many contract and planning prompts. After P50 completed, the focus shifted to generating the remaining prompt queue. Later, after P107 had been generated, the focus shifted from “next prompt” to “what have we done, how many remain, and what is the full plan?” Finally, this archive request shifted the goal again: preserve the state of the chat in a human-readable way for later project writing and aggregation.

The unresolved goals are mostly operational. The chat did not prove the live repository state independently. The user said the live repo was around P95, and the assistant accepted that as a working fact. The chat also did not execute Manual Observation Batch 0, verify hosted deployment, approve connector runtime, or implement later public-alpha systems. Those remain future work.

## 5. Decisions and Commitments

The most important decision was to treat Eureka as an evidence-first temporal object resolver rather than as a generic search engine, app store, downloader, or AI wrapper. This decision appears settled in the chat. It was accepted through repeated use in prompts and the user’s continued direction. It makes sense because archived-object search requires provenance, uncertainty, compatibility, risk, and rights context. The consequence is that every subsystem must carry source/evidence/provenance and must avoid truth claims without review. This could be revisited only if the project’s mission changed fundamentally, but nothing in this chat suggests such a change.

A second major decision was to preserve a static/dynamic separation: static site artifacts can live in `site/dist`, while dynamic public search requires a separate hosted backend. This was presented in the P50 synthesis and later planning. It is treated as settled in the conversation, though the actual hosted deployment state remains unverified in this archive. The rationale is that static hosts such as GitHub Pages cannot run the Python backend. The consequence is that live alpha requires operator deployment work beyond static publication.

A third decision was the blocker-handling correction from the user. Blockers should not make Codex stop and ask for more input in ordinary cases. Instead, prompts must give enough context and rationale for autonomous resolution within safe limits. This is a clear user decision and strongly shaped the prompt style. The consequence is verbose prompts with explicit fallback behavior, allowed bounded repairs, and strict refusal boundaries for unsafe actions.

A fourth decision was to proceed through contracts, planning, local dry-run runtimes, authoritative local stores, and only then public/hosted runtimes or live connectors. This appears to be an accepted architectural commitment, not just a suggestion. It was reflected across P79–P107. The alternative—building live connectors or public search integration immediately—was repeatedly rejected or deferred. The consequence is slower initial feature delivery but much stronger safety and auditability.

A fifth decision was that public search must not perform live source fanout in the early alpha path. It should query controlled public/local indexes only. This is settled across many prompts. The consequence is that search usefulness depends initially on the curated/generated index and later reviewed source-cache/evidence additions, not direct live API calls per user query.

A sixth decision was to make the first live connector path approval-gated and probably start with Internet Archive metadata rather than all connectors at once. This was recommended by the assistant in the broad plan and follows the generated connector planning sequence. It is a strong recommendation rather than a final user-accepted execution decision in this visible chat. It should be treated as tentative until the user explicitly chooses the first connector.

A seventh decision was to pause broad prompt expansion after P107 and focus on execution/consolidation. The assistant recommended this; the user has not explicitly accepted it in the visible transcript before requesting this archive. It should therefore be treated as a recommendation, not a final decision.

## 6. Rejected, Superseded, or Deprioritised Ideas

The chat repeatedly deprioritized direct live connector integration. Calling Internet Archive, Wayback, GitHub, PyPI, npm, or Software Heritage directly from public search was considered too risky and repeatedly forbidden. This status is temporary rather than permanent: live connectors can return later through source-sync workers, cache-first outputs, evidence-ledger candidates, review, and operator approval.

GitHub Pages as a dynamic backend was rejected. The chat treated GitHub Pages as static-only. Dynamic public search needs a separate backend. This rejection is stable unless the hosting architecture changes to a different platform that can run the backend.

AI/model runtime was deprioritized. The plan allows AI assistance only as optional, typed, candidate-generating, disabled-by-default future work. AI cannot decide truth, rights clearance, malware safety, source trust, ranking acceptance, or master-index mutation. This status is temporary but far downstream; AI becomes useful only after deterministic retrieval, evidence, and review systems exist.

Downloads, installers, execution, package managers, emulators, and VM launch were repeatedly forbidden. They are not necessarily never allowed, but they require later action policies, safety review, rights review, malware/risk handling, and likely sandboxing. In this chat they were out of scope for every near-term milestone.

Public contribution intake was deferred. Pack import contracts and local dry-runs are allowed, but public uploads, accounts, moderation, and automatic acceptance were not. This prevents spam, poisoning, rights issues, and unreviewed mutation. It may return after pack quarantine, review queues, abuse policy, and storage policies exist.

External baseline claims were rejected until manual observations exist. The project must not claim superiority over Google, Internet Archive, or other external systems without validated observation records. This is a permanent standard, though the blockage can be resolved by human-operated baseline work.

## 7. Rationale, Tradeoffs, and Design Logic

The visible rationale is conservative but product-oriented. The user wanted real production progress, while the assistant repeatedly built gates to prevent unsafe shortcuts. The main tradeoff is speed versus trust. Directly wiring live APIs into public search would produce visible features faster, but it would create uncontrolled fanout, source-policy risk, rate-limit risk, arbitrary URL risk, and false evidence status. The chosen path—contracts, validators, dry-runs, authoritative stores, then live connectors—is slower but more durable.

Another tradeoff is documentation volume versus implementation velocity. The prompts are long and repetitive because they are intended for autonomous Codex execution. The user explicitly wanted enough context for a clean-room developer to continue without asking. The downside is prompt sprawl and potential over-documentation. The assistant eventually recognized this and recommended a bounded next tranche rather than indefinite expansion.

A third tradeoff is public usefulness versus honesty. A search engine that says “not found” without explaining source gaps is less useful, but a system that fabricates confidence is worse. The plan therefore includes known absence pages, gap explanations, source coverage statuses, manual baselines, and search result explanations. This makes the product more complex but prevents misleading users.

A fourth tradeoff is local dry-run implementation versus authoritative storage. Local dry-runs are useful because they test record loading, classification, validation, and report generation. But dry-runs must not be mistaken for authoritative source cache or evidence ledger runtime. That is why P100 audits public-search integration and why later prompts propose authoritative local runtime planning as a separate step.

The user seems to care most about long-term correctness, autonomous execution, rigorous documentation, and real production readiness. The prompts therefore emphasize Git commits, AIDE metadata, command matrices, validators, tests, command results, and no false claims. If future assistants misunderstand this context, they may either restart brainstorming instead of continuing execution, or worse, treat planning artifacts as implemented behavior.

## 8. Current State at the End of This Chat

At the end of the visible chat, the prompt plan has been generated through P107. The user states that the live repository is still around P95. This repository state is unverified by this archive report. The generated but likely not executed prompts are P96 through P107. The assistant’s last strategic recommendation was that the project should execute P96–P107, then consolidate before generating too far beyond that.

The settled architecture includes evidence-first doctrine, controlled public search, contract and validator layers, dry-run-before-runtime sequencing, connector approval gates, source cache and evidence ledger separation, page/identity/merge/ranking/explanation contracts, and strict no-mutation/no-live-fanout rules for early public search.

Tentative items include the exact prompt count to beta, the exact first connector to implement, the hosting provider choices, the live repository’s current state, and the user’s acceptance of the assistant’s recommendation to pause expansion after P107.

Blocked items include hosted deployment verification, Manual Observation Batch 0, source/API policy review, User-Agent/contact/rate-limit decisions, authoritative source-cache/evidence-ledger storage policy, connector runtime approval, and production-quality claims. These require either human/operator action or repository execution beyond the visible chat.

The next operational move should be to execute the already generated P96–P107 queue if not already live, then run a consolidation audit. After that, P108–P115 should be generated and executed as a bounded next tranche focused on authoritative local runtime planning, public alpha hardening, connector approval decision, hosted page runtime planning refresh, static page snapshots, pack quarantine planning, and deep extraction dry-run runtime only if sandbox approval exists.

## 9. Future Work and Next Steps

The highest-priority next step is to close the gap between generated prompts and live repository execution. If the repo is truly around P95, P96 through P107 should be executed before more broad planning. This matters because those prompts create the missing bridge from contracts to local dry-run runtimes and audits. The expected output is a repo with search result explanation contracts, source/evidence/page/pack/ranking dry-run systems, and integration audits. The risk is that if the queue is skipped, later plans will assume capabilities that do not exist.

The second priority is consolidation after P107. A future prompt should audit what actually landed, not what was generated. It should classify contracts, planning, local dry-runs, public search integration, hosted deployment, source/evidence boundaries, and command status. This prevents planning based on stale assumptions.

The third priority is authoritative local store planning for source cache and evidence ledger. Dry-runs prove shape and reportability, but real connector work needs durable local stores. These plans must define storage format, migrations, rollback, retention, review, and mutation gates. The risk is accidentally turning source-cache records into truth.

The fourth priority is public alpha hardening. Eureka needs a live static site plus hosted backend that safely queries the controlled local/public index. This step depends on hosted deployment verification, edge/rate limits, blocked request tests, health/status routes, privacy/security docs, rollback plans, and no live source fanout. The output should be factual launch evidence, not a marketing claim.

The fifth priority is Manual Observation Batch 0. Human operators must record external baseline observations. This matters because search quality claims and connector prioritization need evidence. The risk is fabricating or overclaiming external comparison results.

The sixth priority is selecting and approving a first live connector path. The assistant recommended Internet Archive metadata as a likely first connector, but this remains tentative. The connector must go through source policy review, User-Agent/contact decisions, rate limits, cache-first output, evidence candidate generation, review, and public index rebuild only after acceptance.

## 10. Artifacts, Files, Prompts, and Outputs

The most important artifacts in this chat are the generated Codex prompts. Each prompt is a self-contained development assignment. They are not merely task names; they contain doctrine, constraints, deliverables, tests, command matrices, commit plans, and final response requirements. These prompts should be preserved because they encode the project’s safety architecture and operational sequencing.

The P50 completion summary, pasted by the user, is another important artifact. It reported three commits, a full post-P49 audit pack, validator and tests, extensive verification results, platform classifications, blockers, and next recommendations. It should be preserved as the first major factual checkpoint in this visible transcript, though its claims are not independently verified here.

The pasted “Eureka mega synthesis for P50 and beyond” is central source material. It explains the product thesis, P49 state, missing areas, P50 audit goals, command matrix, classification system, and a long strategic roadmap. It should feed into any future project book because it captures the transition from prototype/contracts to planned public platform.

The assistant’s broad synthesis after P107 is also important. It explains what had been done, how many prompts remain, and the full phase plan from P96–P107 through public alpha, baselines, source/evidence stores, connectors, pages, ranking, pack import, extraction, and clients. It should be preserved as the current high-level roadmap, with caveats that it includes assistant recommendations and unverified repo-state assumptions.

This archive package itself is also an artifact. It transforms the chat from a long prompt-generation transcript into a human-readable briefing plus structured appendices. It should be used as source material for the larger project book, but not as a substitute for repository verification.

## 11. Open Questions and Unresolved Issues

The first unresolved issue is the exact live repository state. The user states that the live repo is around P95, but this archive did not verify GitHub or local repository contents. This matters because future work depends on knowing which prompts have actually landed. It would be resolved by running a repo audit or checking commits.

The second unresolved issue is hosted deployment. The chat repeatedly treats hosted public search as operator-gated. It is unclear from the visible transcript whether a live backend is configured and verified. This matters because public alpha and hosted runtime planning depend on it. It requires operator verification.

The third unresolved issue is Manual Observation Batch 0. The chat indicates this is likely pending or human-operated. Without it, external baseline comparison and claims about search usefulness remain incomplete. It requires manual human work, not Codex fabrication.

The fourth unresolved issue is which connector should go live first. The assistant recommended Internet Archive metadata as a likely first path, but the user did not explicitly decide in the visible transcript. This requires human/operator approval and source-policy review.

The fifth unresolved issue is authoritative storage policy for source cache and evidence ledger. Dry-runs are useful, but real source/evidence systems need durable storage, rollback, review, and mutation policy. This remains future work.

The sixth unresolved issue is how far to continue prompt generation before execution catches up. The assistant recommended stopping broad expansion after P107 and executing/consolidating. The user has not explicitly accepted or rejected that recommendation in the visible transcript.

## 12. Risks and Failure Modes

One major risk is over-compression. This chat contains many prompts with repetitive but important safety constraints. A future summary that only says “we planned many prompts” would lose the real value: the sequencing logic and the boundaries preventing unsafe behavior. To avoid this, future work should preserve the phase structure and the doctrine.

Another risk is treating generated prompts as completed repository work. P96–P107 are generated, but according to the user the live repo is around P95. Future assistants must distinguish planned prompts from executed commits.

A third risk is treating assistant recommendations as user decisions. The assistant recommended a first connector path and recommended pausing broad prompt expansion after P107. Those are not final user decisions unless later accepted.

A fourth risk is losing the blocker-handling correction. The user’s correction that blockers should be autonomously resolved where safe is central to the prompt design. Future prompts should not revert to asking the user for input on normal repo blockers.

A fifth risk is weakening public search safety. Many future systems—source cache, evidence ledger, pages, ranking, explanations, connectors—could be mistakenly wired into public search too early. P100 exists specifically to audit against this.

A sixth risk is stale external claims. The chat references GitHub Pages limitations, repository state, counts, and workflow statuses from earlier summaries. Unless verified in the repo or web at the time of use, they should be treated as possibly stale.

A seventh risk is merging this chat incorrectly with other chats. This chat is mostly about the prompt queue and architecture; other chats may contain actual repo execution results. Aggregation must separate prompt intent from implementation evidence.

## 13. Larger Project Contribution

This chat contributes a major architectural and operational spine to the Eureka project. Its unique value is not a single code artifact but a carefully sequenced roadmap for moving from prototype to public alpha while preserving evidence, review, and safety. It defines how Codex should work: clean-room prompts, no unsafe live behavior, bounded autonomous blocker resolution, detailed commits, validators, tests, audit packs, and explicit final reports.

It likely overlaps with other chats that generated individual prompts, executed repository work, or discussed deployment. Those chats may contain the actual implementation evidence that this chat lacks. Possible conflicts may arise if another chat claims a later prompt has already landed or if the live repo diverges from the plan. Such conflicts should be resolved by repository state, not by this archive.

For a future book or specification, this chat should contribute the “method and governance” chapter: why Eureka was built as evidence-first, why dry-runs precede runtimes, why public search must be bounded, why connectors are approval-gated, and why manual baselines are required before claims. Some prompt details can become formal requirements after repository review. Other content should remain background context, especially assistant-proposed future prompt numbers beyond P107.

## 14. What To Remember

- Eureka is being designed as an evidence-first temporal object resolver, not a generic search engine, app store, downloader, crawler, or AI answer wrapper.
- The user wanted real production-oriented Codex prompts that could be queued and executed autonomously, with Git/AIDE/validation discipline.
- The user corrected the blocker policy: normal blockers should be resolved autonomously using the prompt’s rationale and constraints, not used as an excuse to stop and ask for input.
- The generated prompt queue reaches P107 in this visible chat, while the user states the live repository is around P95. That repo-state claim is unverified here.
- The plan’s core sequence is contracts → planning → local dry-runs → authoritative local stores → hosted alpha → approved live connectors → pages/explanations/ranking → pack import/deep extraction → clients/offline/federation.
- Public search must remain controlled and local-index-only until explicit later approval. It must not fan out live to external sources.
- Source cache and evidence ledger are separate from truth. They produce records and observations that can become candidates, not accepted facts.
- Manual Observation Batch 0 is human-operated and must not be fabricated by Codex.
- AI/model runtime, downloads, installs, package managers, emulators, uploads, accounts, and public contribution intake are all deferred until later gates.
- The best immediate next action is to execute P96–P107 if not already live, then run a consolidation audit before generating a large new queue.

## 15. Final Plain-English Summary

This chat records a major planning and prompt-generation phase for the Eureka Archive System. The user wanted to build Eureka seriously, not as a prototype experiment or loose idea, but as a real repository moving toward a live public service. The work centered on creating queueable Codex prompts that a powerful coding agent could execute with high autonomy, full repository access, Git discipline, AIDE metadata, validators, tests, and detailed commits. The prompts were intentionally long and explicit because the user wanted them to function as clean-room development instructions: Codex should not need to stop and ask for ordinary missing context, and blockers should be handled by inspecting, classifying, repairing bounded drift, and preserving safety gates.

The main conceptual outcome is that Eureka was framed and repeatedly reinforced as an evidence-first temporal object resolver. That means it should not merely search for files or provide AI answers. It should resolve uncertain digital-object requests into evidence-backed explanations: what the object may be, what versions or representations exist, what source records support it, what conflicts or gaps remain, whether compatibility is known or unknown, and what safe actions are available. The system is designed to preserve uncertainty rather than erase it. It should not claim rights clearance, malware safety, installability, compatibility truth, or source trust unless those claims are specifically reviewed and evidenced.

The chat shows a disciplined architecture emerging across many prompts. P50 established a major audit checkpoint. P51–P58 addressed remediation, static deployment evidence, public search contracts, hosted search planning, index building, static search integration, safety evidence, and hosted rehearsal. P59–P68 built the query-intelligence plane: observations, caches, miss ledgers, search needs, probe queues, candidate indexes, promotion policy, known absence, privacy/poisoning guards, and demand dashboards. P69–P70 defined source sync, source cache, and evidence ledger boundaries. P71–P76 created approval paths for first-wave metadata connectors. P79–P85 designed object pages, source pages, comparison pages, identity resolution, result merge/deduplication, and evidence/compatibility-aware ranking. P86–P92 planned query observation and connector runtimes while preserving approval gates. P93–P95 planned page runtime and pack import and defined deep extraction. P96–P107, generated later, cover search result explanations, ranking planning, local dry-run source/evidence/page/pack/ranking runtimes, integration audits, connector audits, and manual baseline follow-up.

The user later paused and asked where the plan stood. The assistant summarized that prompts had been generated through P107, while the live repo was still around P95 according to the user. That distinction matters. Generated prompts are not the same as executed repository state. The assistant recommended that the project should now execute P96–P107, then consolidate, rather than keep expanding the prompt queue indefinitely. The reason is that Eureka already has a strong contract and planning architecture; the next need is to convert safe planning layers into measured local dry-run runtimes, then authoritative local stores, then a minimal public alpha.

Several commitments should be preserved. Public search should remain bounded and local/public-index-driven until later approval. Dry-run runtimes must not become authoritative stores. Connectors should not be wired into public search or allowed to fan out live. Source cache records are not truth; evidence ledger records are observations; candidates are provisional; master-index mutation requires review. Manual external baseline observations must be performed by humans and cannot be fabricated by Codex. AI/model calls, downloads, installs, package managers, emulators, uploads, accounts, telemetry, public contribution intake, and live connector runtimes are all deferred behind explicit gates.

The unresolved work is substantial. The exact live repository state must be verified. Hosted public deployment remains an operator-gated issue unless later evidence proves otherwise. Manual Observation Batch 0 likely remains pending and blocks external comparison claims. Authoritative source-cache and evidence-ledger storage policies must be designed. A first connector path must be chosen and approved, probably starting with metadata-only Internet Archive if the user accepts that recommendation. Public alpha requires deployment evidence, safety smoke tests, privacy/security/rights documentation, rollback plans, and a controlled local/public index.

For a future book or master project record, this chat is valuable because it captures the governance logic behind Eureka. It explains why the project is not rushing into live crawling, why result explanations and object/source/comparison pages matter, why identity and deduplication must preserve conflicts, why ranking must be explicit and evidence-based, why deep extraction requires sandboxing, and why human baseline observations are needed before quality claims. It should be aggregated as a planning and architecture chapter, not as a repository execution log.

The best next action is to verify the live repository state, execute any missing prompts from P96–P107, and then run a consolidation audit. After that, the next bounded tranche should focus on authoritative local runtime planning, public alpha hardening, connector approval decision, hosted page planning refresh, static snapshots, pack quarantine planning, and deep extraction only after sandbox approval. The project’s safest path remains: build the smallest honest live Eureka first, then expand sources, pages, explanations, ranking, packs, extraction, and clients only after each layer proves itself.

# Reader Status

- Chat title: Eureka Codex Prompt Plan and Production Roadmap
- Report type: human-readable archive report
- Main value of this chat: It preserves the long-range Codex prompt strategy and the safety-gated architecture for moving Eureka from prototype/contracts toward public alpha and later product layers.
- Most important decision: Eureka should proceed through evidence-first, review-gated layers rather than jumping directly to live connectors, AI answers, downloads, or public mutation.
- Most important unresolved issue: The live repository state and hosted deployment status are unverified in this archive; the user states the repo is around P95 while prompts are generated through P107.
- Most important next action: Execute or verify P96–P107, then run a consolidation audit before generating a large new prompt tranche.
- Safe for aggregation: with caveats
- Main caveats: Distinguish generated prompts from implemented repo state; do not treat assistant recommendations as accepted user decisions unless later confirmed; verify live repo/deployment/baseline status before formalizing claims.
