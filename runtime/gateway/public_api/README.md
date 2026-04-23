# Gateway Public API Runtime Boundary

`runtime/gateway/public_api/` contains the transport-neutral runtime support for the draft
public gateway boundary.

Current bootstrap scope:

- submit bounded resolution work and return an accepted envelope with a `job_id`
- read the current in-memory job envelope by `job_id`
- search the bounded software-first corpus through a deterministic public search boundary
- explain bounded exact-resolution and deterministic search misses through a dedicated public absence boundary
- compare exactly two bounded resolved targets through a deterministic public comparison boundary
- list bounded ordered states for one bootstrap subject key through a deterministic public subject/state boundary
- list bounded known representations and access paths for one resolved target through a deterministic public representations boundary
- evaluate one resolved target against one bootstrap host profile preset through a deterministic public compatibility boundary
- select one bounded preferred representation and explicit alternatives for one resolved target through a deterministic public handoff boundary, optionally shaped by one bootstrap host profile preset and one bootstrap strategy profile
- build a bounded action plan for one resolved target, optionally shaped by one bootstrap host profile preset, one bootstrap strategy profile, and bounded local store context
- list bounded manifest-export and bundle-export actions for a resolved bounded target
- export a deterministic machine-readable resolution manifest through the public boundary
- export a deterministic portable resolution bundle through the public boundary
- store deterministic manifest and bundle exports in a local bootstrap content-addressed store
- list stored exports for a target and read stored artifact content by stable artifact identity
- inspect a deterministic portable resolution bundle from local bytes or a local bundle path through a transport-neutral public boundary
- surface a bootstrap deterministic `resolved_resource_id` across resolution, search, actions, stored exports, and bundle inspection where available
- surface bounded source-family and source-origin summaries across resolution, search, export, and stored-export metadata where available
- surface bounded evidence summaries across resolution, search, export, stored-export metadata, and bundle inspection where available
- translate internal gateway job state into public contract-facing envelopes
- map public job envelopes into the shared `WorkbenchSession` view model without
  implementing a web or native shell
- map public search envelopes into a shared search-results view model without
  implementing a web or native shell
- map public comparison envelopes into a shared comparison view model without
  implementing a web or native shell
- map public absence envelopes into a shared absence-report view model without
  implementing a web or native shell
- map public subject/state envelopes into a shared subject/state view model without
  implementing a web or native shell
- map public representations envelopes into a shared representations view model without
  implementing a web or native shell
- map public compatibility envelopes into a shared compatibility view model without
  implementing a web or native shell
- map public handoff envelopes into a shared representation-selection view model without
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
- persistence beyond the local bootstrap filesystem store
- live GitHub acquisition, auth, rate-limit handling, or broader multi-source federation beyond the recorded GitHub Releases fixture slice
- final provenance graph, trust scoring, or cross-source merge behavior beyond the current bounded evidence summary seam
- final comparison, merge, or truth-selection behavior beyond the current bounded disagreement seam
- final object, subject, or state identity behavior beyond the current bounded timeline seam
- final diagnostic or absence-reasoning behavior beyond the current bounded miss-explanation seam
- installers, downloads from external sources, import, restore, rollback behavior, or final representation-selection and handoff semantics
- final compatibility oracle behavior, richer host profile vocabularies, or runtime-routing behavior
- final action-routing policy behavior, user-strategy semantics, execution semantics, installers, or workflow orchestration
- ranking, fuzzy matching, or broader retrieval semantics
- finalized public API guarantees
- finalized global identity or cross-source merge semantics
