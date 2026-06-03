# Human Archive Report — Eureka Search Engine: Corpus Growth, Public UX, and Resilient Search Planning

## 1. Orientation

This chat was a long-running project-planning and handoff session for the Eureka Archive System, focused on moving the project from a structurally correct but thin public alpha toward a usable, governed search engine. The visible conversation was not a single technical question. It was an extended sequence of status reports, planning decisions, prompt generation, corrections, and architectural reframing. The central problem was that Eureka had acquired many pieces of a search/product stack—local workbench, public routes, snapshot/relay projection, source-action planning, candidate indexing, SCOUT relation expansion, review batches, seed batches, and a no-JS public search UX—but the user correctly kept returning to one core issue: a search engine is not useful merely because routes, validators, and candidates exist. It needs a growing, governed corpus of reviewed records, and it needs to remain useful when indexes or other links in the system fail.

The date anchor requested by the user for this archive is 2026-05-31 Australia/Melbourne. The chat itself continued beyond that anchor in visible timestamps and status reports, reaching 2026-06-03 in assistant message headers. This report treats 2026-05-31 as the requested archival anchor while also preserving later visible status changes in the transcript. No outside files or memories were used as authoritative source material for this report. Some earlier uploaded files had expired by the end of the chat, and the report therefore relies on the visible transcript rather than on direct file inspection. Where the transcript states repository statuses or commit hashes, this report records them as FACT in the sense that they were stated in the chat; it does not independently verify the repository.

The user’s practical goal was to steer Eureka toward a modular, portable, extensible, reliable system that could become a real public search engine rather than a one-off prototype, a manually curated index, or a fragile launch demo. The user repeatedly pushed against premature launch, wasted AI/test time, empty public alpha surfaces, overbuilt but underpopulated architecture, and any suggestion that candidate richness should be mistaken for reviewed truth. The project pressure was both technical and operational: tests were taking hours, AI sessions were wasting tokens by waiting on full discovery, and the system’s value was constrained by having very few reviewed records despite a growing candidate and pipeline architecture. The user’s priority ordering was explicit: quality first, token cost second, elapsed time third, with reduced human interaction desirable only if it did not harm quality.

Several large transitions occurred. Early in the visible context, the work was still about dev/main promotion, IA metadata, repo layout, Workbench foundations, source-action architecture, and full-discovery blockers. Then the conversation shifted to test discipline: full discovery was externalized so long-running test runs would be handled by local/CI harnesses rather than by AI polling. Public alpha infrastructure was built, promoted, and launch-gated; then the user rejected the idea of public launch because the system was not yet useful, searchable, or corpus-rich. That rejection became a major product correction. The launch track was deferred, and the project moved into active discovery: Archive.org metadata candidates, a domain-aware query planner, persistent candidate index, SCOUT relation runtime, batch review, frontier-media and legacy-software seed batches, snapshot refreshes, public alpha reassessments, manuals/scans and driver/support seed batches, and eventually a public search UX MVP.

The main outcome of the chat was not a single artifact but a clarified operating model. Eureka should be a temporal object-resolution and evidence-governance system. It should turn messy archival/source observations into explicit object states: verified artifact, reviewed artifact record, reviewed metadata record, reviewed source lead, candidate, known need, bounded absence, near miss, or blocked source. The reviewed-corpus growth loop should be the primary machine: candidate → review → local apply → snapshot refresh → public alpha reassessment. In parallel, the system should gain resilience through indexless live fallback: if reviewed indexes, candidate indexes, source caches, snapshots, or relays are missing, the system should degrade to bounded live metadata candidate lanes rather than failing or pretending to know more than it does.

At the end of this chat, the last completed repository task visible in the transcript was `SNAPSHOT-REFRESH-06`, reported as `PASS_WITH_WARNINGS`, with commit `47425906 feat(snapshot): refresh after review batch apply`. That task integrated review-batch apply outputs into snapshot projections: the limited reviewed projection count rose from 4 to 12, reviewed known needs and bounded absences were projected, and candidate count after apply was 60. The next proposed task was `PUBLIC-ALPHA-REASSESS-06`, to evaluate whether the project should remain deferred after that reviewed-corpus increase. The expected answer was still “not ready for public launch,” because the reviewed record threshold had not been met, reviewed artifact records were still absent, indexless fallback and search usefulness evaluation were not implemented, and external full discovery and main promotion had not been completed after the current dev stack.

A future reader should understand this chat as a strategic hinge. It records Eureka’s movement away from launch-by-infrastructure and toward evidence quality, reviewed corpus growth, resilient degraded search, and explicit public product legibility. It also records many specific task prompts and status reports that can feed later specifications, but the most important contribution is conceptual: the project’s north star became governed object resolution, not simply live Archive.org search or a public alpha route set.

## 2. The Story of the Conversation

The visible conversation begins after a series of repository promotion and validation handoffs. Early statuses described IA metadata work, repo layout canon, and the difficulty of promoting `dev` to `main` while local commits and full-discovery blockers existed. The project repeatedly hit long-running test gates, stale validators, and branch-state issues. The user wanted the assistant to generate improved prompts for Codex-style agents that would reason through blockers rather than stop prematurely. The first arc was therefore about stabilizing the development lane: resolving blockers, promoting dev to main, preserving repo structure boundaries, and making sure tasks had strong boundaries around no deployment, no public launch, no source probing, no download/extraction, no model-provider calls, and no mutation of public/master indexes.

The conversation then broadened into architecture quality. The user asked whether the directory structure, schemas, protocols, APIs, file names, and naming practices were good enough for modularity, extensibility, portability, and future-proofing. The assistant’s visible responses and the user’s later pasted status reports indicate that repo structure and taxonomy work had largely been treated as done enough, with classified debt rather than endless refactoring. The user emphasized that the project should be “a proper app,” not a one-off indie codebase, and the architecture discussions converged on kernels, contracts, projection models, and boundaries between runtime behavior and surfaces.

A major operational correction came when full unittest discovery was still taking roughly an hour. The user objected strongly to AI sessions wasting time and tokens by polling long-running tests. The visible transcript contains a long pasted example of an agent repeatedly reporting that full discovery was still running. The user clarified the priority order: quality first, token reduction second, time reduction third. This led to the `TEST-TOKEN-DISCIPLINE-00` direction: long tests should be run by CI or local harnesses, with compact summaries returned to the AI. The subsequent statuses show that a local/CI full-discovery harness, summarizer, validation scripts, GitHub workflows, and AIDE/agent policies were added. Later, the harness needed UX fixes—heartbeat/progress output, detached run handling, and better logs—because the user could not tell whether a long local command was frozen. This episode mattered because it established that AI should reason over compact artifacts, not babysit slow commands.

The public alpha arc initially moved toward launch. The project built a read-only public alpha foundation, hosting readiness plan, closeout gate, promotion to main, launch candidate gate, deploy dry-run, and a manual launch approval gate. The system could serve local/public-alpha routes and had public read-only page/API foundations. But the user then stopped the launch track. The critical correction was that the public alpha did not yet function as a useful search engine: there were too few things in the index, and the system was not yet discovering results broadly enough. The user explicitly said it was not ready for public alpha and that it needed to actually search sources rather than depend on manual index-building. This changed the roadmap from launch/deploy staging toward active discovery and candidate intake.

After that correction, the chat entered a long constructive buildout. Archive.org metadata candidates were added to public search as review-only candidate lanes. A domain-aware query-to-source-action planner was then implemented so Archive.org searches would be less noisy and more domain-aware. A persistent candidate index followed, so candidates could be stored, deduplicated, searched, and handed to review rather than appear only once. SCOUT runtime then added relation expansion and discovery trails over candidates. Review-batch runtime added candidate clusters, batch decisions, promotion previews, local-apply handoffs, and snapshot refresh handoffs.

With those foundations in place, the project began corpus-building wedges. Frontier-resolution media and legacy-software seed batches were created first. Snapshot refresh packaged those candidates, and reassessment confirmed that public alpha was still not ready because reviewed records were too few. A bounded live metadata pilot over Archive.org was then approval-gated, run with 16 live requests, redacted, and converted into candidate/review handoffs without raw responses, downloads, extraction, accepted truth, or public index mutation. Live metadata candidates were reviewed conservatively, producing previews for one reviewed metadata record and two reviewed source leads. A local-apply task then applied eligible live metadata previews through a temp explicit instance proof, producing limited reviewed metadata/source-lead records without mutating the operator instance or public/master indexes.

The user and assistant then returned to public UX. The user pasted an earlier detailed website/UX analysis that argued the public surface should be search-first, evidence-first, no-JS capable, and based on canonical view models. The assistant accepted the direction but recommended compressing the UX work into model, MVP, and gate tracks rather than launching a twenty-task redesign before continuing discovery. `PUBLIC-SEARCH-UX-MODEL-00` and later `PUBLIC-SEARCH-UX-MVP-00` were completed. The UX MVP added no-JS read-only public pages: home, search, object, candidate, need, source, evidence, status, and no-results/known-need pages. Snapshot refresh 05 then integrated that UX into public projections.

Meanwhile, more seed domains were added. Manuals/scans were chosen as a safer third domain because they reduce executable risk, though still requiring strict no-download, no-OCR, no-rights-claim boundaries. Driver/support was then added as a fourth, higher-risk domain with strict suppression of fake driver updaters, malware/safety claims, compatibility guarantees, downloads, install/execution, and rights clearance. Snapshot refresh 04 integrated those domains, raising total candidates to 68 across four domains. Public alpha reassessments continued to conclude that the system was increasingly useful internally but still not public-launch ready.

Near the end, the user asked whether Eureka now had a website that people could use to search Archive.org and other sites live without the index, and whether it could be designed to work when local and remote indexes are unavailable. The answer was no: the visible system had public UX and live metadata capability, but public live source fanout remained disabled and the system was not yet a public live metasearch website. The assistant proposed an indexless live fallback mode to handle degraded cases. The user then supplied a strong recommendation: the ultimate plan should not be launch-next but reviewed-corpus growth. The assistant agreed, with one addition: keep reviewed-corpus growth as the truth engine and indexless fallback as the resilience engine. The user said “okay proceed,” and the next task generated was `REVIEW-BATCH-APPLY-NEXT-00`. That task completed and was followed by `SNAPSHOT-REFRESH-06`, which raised limited reviewed projection count from 4 to 12. The chat ended before `PUBLIC-ALPHA-REASSESS-06` was executed.

## 3. Main Themes

### Governed object resolution instead of ordinary search

A central theme was that Eureka should not be understood as a generic search box over Archive.org or as a public launcher. The user and assistant converged on a stronger framing: Eureka is a temporal object-resolution system. It should expose object states and evidence states with precision. A result can be verified, candidate, limited reviewed metadata, reviewed source lead, known need, bounded absence, near miss, or blocked source. This matters because archive/source evidence is messy. A metadata hit may prove that a source has a record, but not that a downloadable artifact is complete, safe, rights-cleared, or verified. The chat repeatedly enforced that distinction.

### Candidate richness versus reviewed truth

The project became candidate-rich but reviewed-record poor. This tension drove many reassessments. At different points the snapshot contained 28 candidates, then 36, then 68, while limited reviewed projections slowly rose from 1 to 4 and eventually to 12 after review-batch apply. The user rejected the idea that candidate count alone should justify launch. The project’s near-term objective became moving candidates through review and local apply so reviewed corpus size grows. This theme directly produced the review/apply/snapshot/reassess loop.

### Launch deferral and honest product readiness

The chat repeatedly distinguished route correctness, UX readiness, and public launch readiness. Public alpha routes, read-only APIs, hosting readiness, deployment dry-runs, and UX pages were all useful, but none of them created public launch readiness. Launch remained deferred because the reviewed corpus was thin, artifact verification was absent, external full discovery had not run after the current dev stack, dev had not been promoted after later work, and no manual launch approval existed. The recurring message was: do not launch from infrastructure, candidates, previews, or hopes.

### Test discipline and AI cost control

The user objected to AI wasting time and tokens by waiting on full unittest discovery. This became a defining operational theme. The project added external full-discovery harnesses, compact summaries, CI/manual workflows, progress heartbeat, and agent policies. The quality principle was explicit: quality first, tokens second, time third. Full discovery should be a machine/CI artifact-producing gate, not an interactive AI babysitting loop. This theme informs future task prompts: focused tests inside AI, full discovery outside AI.

### Modular, portable, extensible architecture

The user repeatedly asked whether the repo structure, protocols, APIs, schemas, names, and directories were future-proof, modular, portable, and appropriate for a proper app. The visible conversation preserved a strong architecture rule: kernels own behavior, contracts own meaning, surfaces own rendering, policies own permissions, stores own persistence, and validators enforce boundaries. The system should be able to replace files/directories/components without collapsing into a one-off script network.

### Public UX as evidence cockpit

The UX discussions framed Eureka as “classic search plus evidence cockpit.” The public surface should be search-first, no-JS capable, minimal, and legible. It should show result status, evidence reason, confidence/uncertainty, risk/rights/compatibility posture, and next safe action. Candidates must not look verified. No-results pages should become known-need/coverage/next-action pages, not dead ends. This led to public search view models and a public search UX MVP.

### Resilience and indexless fallback

Late in the chat, the user asked whether the system could work when local and remote indexes are unavailable. The assistant answered that this was not yet built and proposed an indexless live metadata fallback. This became a major unresolved design theme. The truth engine grows reviewed corpus; the resilience engine should make the system useful when indexes or relays fail by using connector capability negotiation and bounded live metadata lanes.

## 4. What We Were Actually Trying To Achieve

The explicit user goal changed over time but remained coherent. At first, the user wanted increasingly robust Codex prompts and branch/task plans so the repo could move safely from IA metadata, Workbench, and source architecture toward public alpha. Later, the user wanted to stop wasting AI and token time on long test runs. Then the user wanted to stop premature launch and make the system actually find useful results. By the end, the user wanted a plan that would create a modular, extensible, reliable search engine capable of working even when parts of the indexing chain fail.

A major inferred goal is that the user wants Eureka to be both a product and a long-term research/engineering system. The visible chat repeatedly returned to “proper app,” future-proofing, portability across projects, reusable components, and a public-facing search experience. This is an INFERENCE because the user stated many pieces of this directly but did not formally define a single product charter inside this chat.

Another inferred goal is cost control without quality loss. The user’s test-harness frustration and priority ordering show that the system should be designed so machines do long validation, AI reasons over summaries, and human interaction is reduced only when it does not undermine correctness.

Goals that changed included public alpha launch. Earlier tasks moved toward launch, staging, and deployment rehearsal. The user later rejected launch as premature because the system did not actually search enough or have enough reviewed corpus. That changed the goal from “get public alpha out” to “build the discovery/review/corpus machine.”

Goals still unresolved include public live search, indexless fallback, reviewed artifact records, a search usefulness eval set, external full discovery after the current dev stack, promotion to main after the current work, and any public launch approval.

## 5. Decisions and Commitments

The most important decision was to defer public launch. This was accepted by the user after observing that the public alpha did not function as a useful search engine and had too few reviewed records. The alternative was to proceed with staging/public alpha based on route correctness and dry-run gates. That alternative was rejected because it would expose a thin product and risk misleading testers. The decision remains active at the end of the chat.

A second major decision was to make reviewed-corpus growth the main machine. The user explicitly recommended that Eureka stop treating launch as the next milestone and focus on turning candidates into governed reviewed records. The assistant agreed. This decision is visible and accepted. Its consequence is the review/apply/snapshot/reassess heartbeat. It could be revisited if launch requirements change or if indexless live fallback becomes sufficient for a different kind of public demo, but the chat’s visible logic strongly favors reviewed corpus growth.

A third decision was to externalize long-running full discovery. The user objected to AI polling tests. The project added harnesses and policies so full discovery produces compact artifacts outside the model loop. This is settled operational doctrine in this chat.

A fourth decision was that public UX must be no-JS, search-first, read-only, and view-model based. This was implemented through `PUBLIC-SEARCH-UX-MODEL-00`, `PUBLIC-SEARCH-UX-MVP-00`, and `SNAPSHOT-REFRESH-05`. It is settled as the current public surface direction, though further UX gates remain possible.

A fifth decision was that Archive.org metadata and other source observations should remain candidate/review evidence, not automatic truth. This is a pervasive boundary across the chat. It is not tentative.

A sixth decision was to keep downloads, extraction, OCR, installs, model-provider behavior, public mutation, and public live fanout disabled unless future explicit gates approve them. This was repeatedly enforced across tasks and remains active.

A seventh decision was to add indexless live fallback soon, but not to treat it as already built. This is a proposed next track rather than completed work. The user asked whether such a design was possible; the assistant recommended it; the user then accepted a plan where review-batch apply came first and indexless fallback would follow soon. Status: planned, not implemented.

## 6. Rejected, Superseded, or Deprioritised Ideas

Public alpha launch was rejected for now. It had been supported by launch-candidate and deploy-dry-run evidence, but the user rejected it because the product did not search enough and the reviewed corpus was too thin. This is a temporary rejection: launch may return after reviewed record thresholds, UX gates, full discovery, main promotion, publication rehearsal, and manual approval.

A broad “search all the web” framing was rejected or refined. The user initially said the system needed to search all the web because manual index-building was not working. The assistant reframed this as source-action planning, connector capability, bounded metadata sources, review-required candidate lanes, and eventually indexless fallback—not arbitrary crawling or scraping. That broad phrase remains an aspiration for usefulness, not a literal accepted implementation plan.

AI babysitting long tests was rejected. The transcript’s pasted “still running” loop became a negative example. The replacement is local/CI harnessing with compact summaries.

Endless directory refactoring was deprioritized. Earlier reports stated the repo structure was fit for purpose with classified debt. Further structure work was judged lower value than product architecture and corpus growth.

More seed domains were temporarily deprioritized after manuals/scans and driver/support. The user’s later recommendation said not to keep adding seed domains before review throughput improves. This does not mean no more domains ever; it means reviewed-corpus growth should now take precedence.

Treating reviewed metadata/source leads as verified artifacts was rejected. This boundary is central. Limited records improve usefulness but do not prove artifacts, downloads, safety, compatibility, or rights.

Public live source fanout was not accepted. The system has live metadata capability, but public live fanout remains false. Indexless fallback is planned, but it must be policy-gated and candidate-only.

## 7. Rationale, Tradeoffs, and Design Logic

The most important tradeoff is between usefulness and truthfulness. A search engine that returns many live candidates may feel useful, but if it presents candidates as reviewed objects it becomes untrustworthy. A strictly reviewed-only search may be trustworthy but empty. The chosen design balances this by showing multiple lanes: reviewed records, limited metadata/source leads, candidates, needs, absences, blocked/deferred sources, and eventually live fallback. This preserves usefulness without collapsing uncertainty.

A second tradeoff is between launch speed and long-term credibility. Public alpha infrastructure existed, but launching too early would test the wrong thing: users would judge Eureka as an empty or confusing search engine. The project instead chose to build corpus growth and UX legibility first.

A third tradeoff is between AI autonomy and token/time efficiency. AI can help generate prompts, reason over blockers, and synthesize plans, but it should not sit idle while tests run. The harness approach lets quality remain high without burning tokens.

A fourth tradeoff is between modularity and task overhead. The chat created many tasks, validators, policies, matrices, docs, and audit packs. This can feel heavy, but it supports the user’s desire for portable, modular, extensible code. The risk is process bloat. The visible answer to that risk is to keep tasks focused on real bottlenecks: review throughput, indexless fallback, search eval, artifact gates.

The user’s priorities were clear: quality comes first, then token cost, then elapsed time. This implies future assistants should not propose shortcuts that risk correctness, and should not compress away important boundaries merely to be faster.

If this context is misunderstood, future work could repeat old mistakes: launching from candidate richness, treating live metadata as truth, adding another seed domain instead of applying review batches, running full discovery inside AI, or building public live search without coverage/status/failure lanes.

## 8. Current State at the End of This Chat

FACT from visible chat: the latest completed repository task reported before the archive request is `SNAPSHOT-REFRESH-06`, with status `PASS_WITH_WARNINGS`, commit `47425906 feat(snapshot): refresh after review batch apply`, `dev == origin/dev`, and a clean working tree. The warning was advisory AIDE verify context-reference warnings, 0 errors.

FACT from visible chat: after `SNAPSHOT-REFRESH-06`, limited reviewed projection count is reported as 12. Candidate count after apply is 60. Reviewed known needs and reviewed bounded absences are 2 each. The project still has no deployment, no public launch, no production/public readiness claim, no site/dist write, no public mutation, no public live source fanout, no downloads, no file fetches, no OCR, no extraction, and no model-provider use.

FACT from visible chat: the next proposed task is `PUBLIC-ALPHA-REASSESS-06`, but it has not been reported as completed in the visible chat. The user then asked for this archive report.

Settled: launch remains deferred; public UX MVP exists; reviewed-corpus growth loop is working; full discovery should not run inside AI; live metadata remains candidate/review-bound; public mutation and public live fanout remain disabled.

Tentative/planned: indexless live fallback, search usefulness eval, reviewed artifact gate, external full discovery after the current dev stack, dev-to-main promotion, snapshot publication rehearsal, and any public alpha launch.

Blocked: public launch is blocked by reviewed corpus depth, absence of reviewed artifact records, missing indexless fallback, missing search usefulness eval, missing external full discovery after current stack, current stack not yet promoted to main, and no public launch approval.

## 9. Future Work and Next Steps

The immediate next step should be `PUBLIC-ALPHA-REASSESS-06`. Its purpose is to evaluate the effect of `SNAPSHOT-REFRESH-06`: reviewed projection count rose from 4 to 12, but launch likely remains deferred. It should produce an updated blocker register and next-work recommendation. It must not deploy, launch, mutate public indexes, or claim readiness.

After that, the next high-priority task should likely be `INDEXLESS-LIVE-SEARCH-FALLBACK-00`, as recommended in the last assistant plan. This would make search resilient when reviewed indexes, candidate indexes, source caches, snapshots, or relays are unavailable. It should use connector capability negotiation and live metadata candidate lanes, not public truth.

`SEARCH-USEFULNESS-EVAL-00` should also be near-term. The project needs a 30–50 query eval set that measures useful outcomes, not just candidate count. This should track reviewed hits, candidate help, known needs, absences, false positives, unsafe suppressions, coverage clarity, and time to useful lane.

`REVIEWED-ARTIFACT-RECORD-GATE-00` should be separate. It should define how a result can become a reviewed artifact record without conflating artifact identity with malware-clean, rights-cleared, or download-safe claims.

External full discovery remains needed before promotion or launch. It should run through the external harness, not inside AI.

Dev-to-main promotion should come only after current dev stack passes the required gate. Public launch requires additional manual approval and likely a snapshot publication rehearsal.

## 10. Artifacts, Files, Prompts, and Outputs

This chat contains many prompts and task handoffs rather than direct file uploads. The important “artifacts” are mostly repository tasks, generated task prompts, and reported commits/statuses.

The test harness work is central. It introduced scripts and workflows for external full discovery, compact summary generation, failed-test reruns, GitHub Actions, and AIDE/agent policy updates. Its substance is not a specific file list here but an operating rule: AI should not babysit full discovery.

The public alpha launch/defer artifacts matter because they record the change in product direction. Public alpha launch candidate and deploy dry-run evidence existed, but the launch track was deferred because the product was not yet useful enough.

The active discovery stack artifacts include source-action kernel, Archive.org metadata candidate path, query planner, candidate index runtime, SCOUT runtime, review batch runtime, seed batches, live metadata pilot, local apply, and snapshots/reassessments. These should feed future book chapters about building a governed search engine.

The UX artifacts include public search view models, public search UX MVP pages, result cards, status badges, no-results behavior, accessibility/no-JS matrices, and snapshot projection refreshes. They should be preserved for product/design chapters.

The latest operational artifacts are `REVIEW-BATCH-APPLY-NEXT-00`, `SNAPSHOT-REFRESH-06`, and the proposed `PUBLIC-ALPHA-REASSESS-06`. These represent the current heartbeat of reviewed-corpus growth.

## 11. Open Questions and Unresolved Issues

The most important unresolved issue is whether Eureka can reach a sufficient reviewed corpus. The current limited reviewed projection count is 12, below the repeatedly cited threshold of 25. The threshold itself is a policy estimate visible in the chat, not an externally verified product truth.

Indexless live fallback remains unimplemented. The user explicitly asked about running when indexes are unavailable. The answer was that this is not yet built. It matters for reliability and user-perceived usefulness.

Search usefulness evaluation remains unimplemented. Candidate count and reviewed count are insufficient product KPIs. The system needs a hard query eval set.

Reviewed artifact record gating remains unimplemented. The system has limited reviewed metadata/source-lead records but not a governed path for verified artifact records.

External full discovery after the current dev stack remains pending. The chat’s status reports consistently avoid running full discovery inside AI. This is appropriate, but it means promotion and launch gates still need external validation.

Main promotion after the current work remains unresolved. Many tasks are on dev; promotion state at the very end is not independently verified beyond visible statuses.

Public launch remains unapproved and not recommended. It would require explicit manual approval, deployment details, publication rehearsal, full discovery, and probably a larger reviewed corpus.

## 12. Risks and Failure Modes

A future assistant may over-compress the chat into “Eureka built a public search site.” That would be wrong. The system has a public search UX MVP and projections, but public launch remains deferred and public live fanout remains disabled.

A future assistant may treat candidates as reviewed truth. This is the largest semantic risk. The chat repeatedly distinguishes candidates, limited reviewed metadata, source leads, reviewed needs, bounded absences, and verified artifacts.

A future assistant may treat the assistant’s proposed prompts as completed work. Only user-provided status reports should be treated as completed tasks. For example, `PUBLIC-ALPHA-REASSESS-06` was proposed but not completed in the visible chat.

A future assistant may repeat the rejected launch path. Public alpha launch was intentionally deferred even after launch candidate and deploy dry-run work.

A future assistant may run full discovery inside AI. This contradicts the test-token discipline established in the chat.

A future assistant may ignore expired files. Some uploaded files expired; file-level facts should not be invented from them.

A future assistant may assume repository commit statuses are independently verified. They are visible status reports, not tool-verified facts in this archive.

## 13. Larger Project Contribution

This chat contributes a major chapter to the Eureka project: the transition from infrastructure readiness to governed corpus growth. It shows how the project resisted premature launch, built an active discovery stack, grew candidate coverage across four domains, added public UX, and then refocused on review/apply throughput and resilience.

It likely overlaps with other chats about repo structure, Workbench, IA metadata, public alpha, and UX design. Possible conflicts may arise if another chat treats public launch as closer than this chat does, or treats live search as already public-enabled. This chat’s position is stricter: public launch is still deferred.

Material that could become formal requirements after review includes the object-state model, the review/apply/snapshot/reassess heartbeat, full-discovery externalization, public UX no-JS/read-only requirements, and indexless fallback requirements. Material that should remain background until implemented includes exact future task ordering, reviewed record thresholds, and launch gates.

## 14. What To Remember

- Eureka’s current north star in this chat is governed temporal object resolution, not generic archive search.
- Public alpha launch is deferred despite substantial infrastructure and UX work.
- The reviewed-corpus loop is now the main machine: review, apply, snapshot, reassess.
- Full discovery should run outside AI through harness/CI summaries.
- Candidates are not truth; metadata hits are evidence; limited reviewed metadata/source leads are not verified artifacts.
- The latest completed state is `SNAPSHOT-REFRESH-06`, with 12 limited reviewed projections and 60 remaining candidates.
- The next proposed task is `PUBLIC-ALPHA-REASSESS-06`, not yet completed in the visible chat.
- Indexless live fallback is a major planned resilience task, not yet implemented.
- Search usefulness eval and reviewed artifact gate are important missing quality gates.
- Future assistants must not treat launch, public live fanout, downloads, extraction, OCR, model calls, or public index mutation as enabled.

## 15. Final Plain-English Summary

This chat captured the Eureka project in a transitional and strategically important stage. The user began from a project that had already accumulated many repository tasks, validators, source/action layers, and public-alpha scaffolding. The early visible context was full of branch-state gates, IA metadata promotion, repo layout classification, Workbench foundations, search interaction contracts, candidate lanes, and repeated validation reports. But the conversation’s deeper purpose became clear only as the user challenged the project’s direction: it was not enough to have routes, validators, and a local public-alpha surface if the system did not actually produce useful search results and governed reviewed records.

A major early problem was test execution. Full unittest discovery was taking roughly an hour, and the user objected to the waste of AI time and tokens. The chat established a strong operational rule: long-running full discovery must run outside the AI loop, via local or CI harnesses that produce compact summaries. AI should inspect the summaries, classify failures, and propose fixes; it should not sit there polling. This became part of the project’s engineering culture: quality first, token cost second, elapsed time third.

The next major shift was the public alpha correction. The project had moved through read-only public alpha routes, hosting readiness, closeout, launch-candidate gate, deploy dry-run, and a manual approval gate. But the user stopped the launch track because the product did not yet work as a useful search engine. There were too few reviewed records and too much manual index-building. Launching would have exposed a shell rather than a useful product. This was one of the most important decisions in the chat: public launch was deferred, and the project turned toward active discovery and candidate intake.

That led to a long buildout of the discovery/review stack. Archive.org metadata candidates were added, followed by a domain-aware query planner, persistent candidate indexing, SCOUT relation expansion, review batch workflow, and seed batches for frontier-resolution media and legacy software. Later, manuals/scans and driver/support seed batches expanded the domain coverage to four areas. A bounded operator-approved live metadata pilot over Archive.org produced real source-backed candidates without raw response commits, downloads, extraction, or accepted truth. Those candidates were reviewed conservatively, some became preview records, and a local-apply task proved that eligible previews could become limited reviewed metadata/source-lead records in a temporary explicit instance without mutating operator, public, or master indexes.

The public-facing side also matured. The user raised a strong UX concern: before public alpha, the site needed to be search-first, no-JS capable, evidence-first, and legible. The project added canonical public search view models and a public search UX MVP, with home, search, object, candidate, need, source, evidence, status, and no-results/known-need pages. Snapshot refreshes then projected the UX and domain/candidate/record states into public-relay material. This improved the internal demo and review value of the system, but it did not make public launch appropriate.

The final completed operational state visible in the chat is `SNAPSHOT-REFRESH-06`. It packages the results of a review-batch apply: 68 candidates were considered, 12 were eligible for apply, 8 limited reviewed records were added, and the total limited reviewed projection count rose from 4 to 12. It also preserved two reviewed known needs and two reviewed bounded absences. Sixty candidates remain non-applied. The boundaries stayed intact: no deployment, no public launch, no site/dist write, no public live fanout, no downloads, no file fetches, no OCR, no extraction, no model-provider use, no artifact verification, no malware-clean claims, no compatibility guarantees, no rights-clearance claims, and no public/master index mutation.

The next proposed task is `PUBLIC-ALPHA-REASSESS-06`, which should evaluate this improved state. The expected result is still not launch-ready. Twelve limited reviewed projections are a meaningful improvement, but they remain below the cited launch threshold of 25 reviewed records, and they are not reviewed artifact records. The project still lacks indexless live fallback, search usefulness evaluation, a reviewed artifact gate, external full discovery after the current stack, main promotion after the current dev work, snapshot publication rehearsal, and manual public launch approval.

The most important larger conclusion is that Eureka’s best path is no longer “build more launch paperwork” or “add more seed domains indefinitely.” The best path is to make reviewed-corpus growth the central machine. The heartbeat should be: review candidates, apply eligible ones through local gates, refresh snapshots, reassess public usefulness, and repeat. In parallel, Eureka should add indexless live fallback so search can remain useful when indexes, snapshots, relays, or caches are unavailable. Those two engines—truth growth and resilience—are the project’s next strategic foundation.

Future assistants should preserve the distinctions established here. Candidate richness is not truth. Metadata is evidence, not artifact verification. Limited reviewed metadata/source-lead records are useful, but they do not prove a file is safe, complete, rights-cleared, compatible, downloadable, or installable. Public search UX makes results legible, but it does not create corpus depth. Public launch remains deferred until reviewed corpus, artifact gating, resilience, external validation, main promotion, publication rehearsal, and manual approval all support it.

# Reader Status

- Chat title: Eureka Search Engine: Corpus Growth, Public UX, and Resilient Search Planning
- Report type: human-readable archive report
- Main value of this chat: It records the shift from public-alpha launch readiness to governed reviewed-corpus growth and resilient search design.
- Most important decision: Defer public launch and make candidate → review → local apply → snapshot → reassess the core engine.
- Most important unresolved issue: Eureka still lacks sufficient reviewed corpus depth, reviewed artifact records, indexless live fallback, and search usefulness evaluation.
- Most important next action: Execute `PUBLIC-ALPHA-REASSESS-06`, then proceed toward `INDEXLESS-LIVE-SEARCH-FALLBACK-00` and `SEARCH-USEFULNESS-EVAL-00` after preserving the reviewed-corpus loop.
- Safe for aggregation: yes, with caveats
- Main caveats: Repository statuses are visible chat reports rather than independently verified tool outputs; some uploaded files expired; proposed prompts must not be treated as completed work unless the user reported completion.
