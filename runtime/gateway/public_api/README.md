# Gateway Public API Runtime Boundary

`runtime/gateway/public_api/` contains the transport-neutral runtime support for the draft
public gateway boundary.

Current bootstrap scope:

- submit bounded resolution work and return an accepted envelope with a `job_id`
- read the current in-memory job envelope by `job_id`
- search the bounded software-first corpus through a deterministic public search boundary
- plan one bounded raw query through a deterministic public query-planner boundary, including old-platform platform constraints, latest-compatible intent, driver/hardware hints, vague identity uncertainty, documentation intent, member-discovery hints, and suppression hints when present
- build, inspect, and query one bootstrap local SQLite index through a deterministic public local-index boundary
- run Archive Resolution Eval Runner v0 through a deterministic public eval boundary, returning bounded suite and task result envelopes without implying background execution, ranking, fuzzy retrieval, vector search, LLM planning, crawling, live sync, or production benchmark semantics
- create, read, and list synchronous bootstrap local tasks through a deterministic public local-tasks boundary
- start, read, and list synchronous local exact-resolution, deterministic-search, and planned-search runs through a deterministic public resolution-runs boundary
- create, read, and list explicit local resolution-memory records derived from persisted runs through a deterministic public resolution-memory boundary
- start one synchronous local planned-search run that persists an optional `resolution_task` summary alongside the current deterministic-search investigation record
- explain bounded exact-resolution and deterministic search misses through a dedicated public absence boundary
- compare exactly two bounded resolved targets through a deterministic public comparison boundary
- list bounded ordered states for one bootstrap subject key through a deterministic public subject/state boundary
- list bounded known representations and access paths for one resolved target through a deterministic public representations boundary
- list governed source-registry records and read one source-registry record by id through a deterministic public source-registry boundary, including bounded capability and coverage-depth metadata without exposing private local paths
- evaluate one resolved target against one bootstrap host profile preset through a deterministic public compatibility boundary
- select one bounded preferred representation and explicit alternatives for one resolved target through a deterministic public handoff boundary, optionally shaped by one bootstrap host profile preset and one bootstrap strategy profile
- fetch one explicitly chosen bounded representation payload for one resolved target through a deterministic public acquisition boundary
- inspect one explicitly chosen fetched bounded representation into a compact member listing through a deterministic public decomposition boundary
- read one explicitly chosen bounded member from one explicitly chosen fetched representation through a deterministic public member-access boundary
- build a bounded action plan for one resolved target, optionally shaped by one bootstrap host profile preset, one bootstrap strategy profile, and bounded local store context
- list bounded manifest-export and bundle-export actions for a resolved bounded target
- export a deterministic machine-readable resolution manifest through the public boundary
- export a deterministic portable resolution bundle through the public boundary
- store deterministic manifest and bundle exports in a local bootstrap content-addressed store
- list stored exports for a target and read stored artifact content by stable artifact identity
- inspect a deterministic portable resolution bundle from local bytes or a local bundle path through a transport-neutral public boundary
- surface a bootstrap deterministic `resolved_resource_id` across resolution, search, actions, stored exports, and bundle inspection where available
- surface bounded synthetic member records, including deterministic member target refs, member paths, parent target refs, parent representation ids, member kind, evidence, and action hints where available
- surface bounded source-family and source-origin summaries across resolution, search, export, and stored-export metadata where available
- surface bounded evidence summaries across resolution, search, export, stored-export metadata, and bundle inspection where available
- translate internal gateway job state into public contract-facing envelopes
- map public job envelopes into the shared `WorkbenchSession` view model without
  implementing a web or native shell
- map public search envelopes into a shared search-results view model without
  implementing a web or native shell
- map public resolution-runs envelopes into a shared resolution-run view model without
  implementing a web or native shell
- map public query-plan envelopes into a shared query-plan view model without
  implementing a web or native shell
- map public local-index envelopes into a shared local-index view model without
  implementing a web or native shell
- map public archive-resolution eval envelopes into a shared eval-report view model without
  implementing a web or native shell
- map public local-task envelopes into a shared local-task view model without
  implementing a web or native shell
- map public resolution-memory envelopes into a shared resolution-memory view model without
  implementing a web or native shell
- map public comparison envelopes into a shared comparison view model without
  implementing a web or native shell
- map public absence envelopes into a shared absence-report view model without
  implementing a web or native shell
- map public subject/state envelopes into a shared subject/state view model without
  implementing a web or native shell
- map public representations envelopes into a shared representations view model without
  implementing a web or native shell
- map public source-registry envelopes, including capability and coverage-depth fields, into a shared source-registry view model without
  implementing a web or native shell
- map public compatibility envelopes into a shared compatibility view model without
  implementing a web or native shell
- map public handoff envelopes into a shared representation-selection view model without
  implementing a web or native shell
- map public acquisition envelopes into a shared acquisition view model without
  implementing a web or native shell
- map public decomposition envelopes into a shared decomposition view model without
  implementing a web or native shell
- map public member-access envelopes into a shared member-access view model without
  implementing a web or native shell
- map public action-plan envelopes into a shared action-plan view model without
  implementing a web or native shell
- map public action envelopes into a shared action-panel view model without
  implementing a web or native shell
- map public stored-export envelopes into a shared stored-exports view model without
  implementing a web or native shell
- map public bundle inspection envelopes into a shared inspection view model without
  implementing a web or native shell
- expose narrow bootstrap demo composition helpers so current surfaces can bootstrap public APIs without importing non-public gateway modules directly
- stay mechanically separated from `surfaces/**` by the repo-local architecture-boundary checker

Out of scope here:

- owning HTTP serving directly inside gateway; the current local stdlib HTTP API slice remains surface-owned under `surfaces/web/server/`
- async workers or orchestration
- persistence beyond the local bootstrap filesystem store, local bootstrap resolution-run JSON store, local bootstrap resolution-memory JSON store, local bootstrap task-store JSON records, and caller-provided bootstrap local SQLite index path
- worker queues, background schedulers, or async orchestration for resolution runs
- worker queues, background schedulers, retries, priorities, or distributed queue behavior for local tasks
- automatic memory creation, shared/cloud memory, invalidation engines, or personalization behavior for resolution memory
- incremental indexing, ranking, fuzzy matching, vector search, semantic recall, or planner-driven retrieval routing for local index queries
- ranking, fuzzy matching, vector search, semantic recall, LLM planning, crawling, live source sync, or production relevance claims for archive-resolution eval execution
- full investigation planning, planner-owned retrieval routing, phases, checkpoints, or streaming transport for resolution runs
- implying that old-platform planner hints perform ranking, fuzzy/vector retrieval, LLM planning, live source behavior, or planner-owned result routing
- exposing raw fixture paths or private local paths through the public source-registry boundary
- implying that source capability metadata implements a connector, live probe, crawl, or source-sync path
- implying that recorded Internet Archive fixtures are a live Internet Archive connector or that local bundle fixtures are arbitrary local filesystem ingestion
- implying that synthetic member records are broad extraction, arbitrary local filesystem indexing, ranking, or final object-identity semantics
- live GitHub acquisition, auth, rate-limit handling, or broader multi-source federation beyond the recorded GitHub Releases fixture slice
- final provenance graph, trust scoring, or cross-source merge behavior beyond the current bounded evidence summary seam
- final comparison, merge, or truth-selection behavior beyond the current bounded disagreement seam
- final object, subject, or state identity behavior beyond the current bounded timeline seam
- final diagnostic or absence-reasoning behavior beyond the current bounded miss-explanation seam
- installers, downloads from external sources, import, restore, rollback behavior, or final representation-selection, handoff, acquisition, decomposition, or member-readback semantics
- final compatibility oracle behavior, richer host profile vocabularies, or runtime-routing behavior
- final action-routing policy behavior, user-strategy semantics, execution semantics, installers, or workflow orchestration
- ranking, fuzzy matching, vector retrieval, or broader retrieval semantics
- finalized public API guarantees
- finalized global identity or cross-source merge semantics
