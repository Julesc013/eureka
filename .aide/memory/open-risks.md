# Eureka AIDE Open Risks

- This is the first real target-repo import; target adaptation may expose pack assumptions that were invisible inside AIDE.
- Eureka-specific golden tasks are not yet established, so quality evidence is limited to AIDE Lite substrate checks and packet review.
- No provider routing, Gateway forwarding, model-call enforcement, or autonomous loop is enabled in this pilot.
- Token measurement uses the approximate `chars / 4` method, not an exact tokenizer or provider billing integration.
- Imported pack commands may need upstream synchronization after the Eureka-local selftest fallback repair; this target task does not mutate the AIDE source repo.
- Eureka-local AIDE Lite `test` and `selftest` now pass after the temp-fixture fallback repair, but broad trust still needs Eureka-specific golden tasks.
- First real follow-up should add deterministic Eureka-specific AIDE golden tasks before broader product implementation work.
