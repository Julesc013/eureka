# Gateway Public API Runtime Boundary

`runtime/gateway/public_api/` contains the transport-neutral runtime support for the draft
public gateway boundary.

Current bootstrap scope:

- submit bounded resolution work and return an accepted envelope with a `job_id`
- read the current in-memory job envelope by `job_id`
- search the governed synthetic software corpus through a deterministic public search boundary
- list bounded manifest-export and bundle-export actions for a resolved synthetic target
- export a deterministic machine-readable resolution manifest through the public boundary
- export a deterministic portable resolution bundle through the public boundary
- store deterministic manifest and bundle exports in a local bootstrap content-addressed store
- list stored exports for a target and read stored artifact content by stable artifact identity
- inspect a deterministic portable resolution bundle from local bytes or a local bundle path through a transport-neutral public boundary
- surface a bootstrap deterministic `resolved_resource_id` across resolution, search, actions, stored exports, and bundle inspection where available
- translate internal gateway job state into public contract-facing envelopes
- map public job envelopes into the shared `WorkbenchSession` view model without
  implementing a web or native shell
- map public search envelopes into a shared search-results view model without
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

- real HTTP serving
- async workers or orchestration
- persistence beyond the local bootstrap filesystem store
- installers, downloads from external sources, import, restore, or rollback behavior
- ranking, fuzzy matching, or broader retrieval semantics
- finalized public API guarantees
- finalized global identity or cross-source merge semantics
