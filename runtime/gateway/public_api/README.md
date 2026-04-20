# Gateway Public API Runtime Boundary

`runtime/gateway/public_api/` contains the transport-neutral runtime support for the draft
public gateway boundary.

Current bootstrap scope:

- submit bounded resolution work and return an accepted envelope with a `job_id`
- read the current in-memory job envelope by `job_id`
- search the governed synthetic software corpus through a deterministic public search boundary
- translate internal gateway job state into public contract-facing envelopes
- map public job envelopes into the shared `WorkbenchSession` view model without
  implementing a web or native shell
- map public search envelopes into a shared search-results view model without
  implementing a web or native shell

Out of scope here:

- real HTTP serving
- async workers or orchestration
- persistence
- ranking, fuzzy matching, or broader retrieval semantics
- finalized public API guarantees
