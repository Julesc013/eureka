# Eureka AIDE Open Risks

- This is the first real target-repo import; target adaptation may expose pack assumptions that were invisible inside AIDE.
- Eureka-specific golden tasks now exist and pass, but they prove deterministic governance readiness rather than arbitrary product implementation quality.
- No provider routing, Gateway forwarding, model-call enforcement, or autonomous loop is enabled in this pilot.
- Token measurement uses the approximate `chars / 4` method, not an exact tokenizer or provider billing integration.
- Imported pack commands may need upstream synchronization after the Eureka-local selftest fallback repair; this target task does not mutate the AIDE source repo.
- Eureka-local AIDE Lite `test`, `selftest`, and `eval run` pass after target repairs, but broad product automation is still deferred.
- First real follow-up should be one bounded docs/eval/architecture-maintenance task before connector, gateway, native, runtime, or broad product work.
