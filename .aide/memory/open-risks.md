# Eureka AIDE Open Risks

- This is the first real target-repo import; target adaptation may expose pack assumptions that were invisible inside AIDE.
- Eureka-specific golden tasks are not yet established, so quality evidence is limited to AIDE Lite substrate checks and packet review.
- No provider routing, Gateway forwarding, model-call enforcement, or autonomous loop is enabled in this pilot.
- Token measurement uses the approximate `chars / 4` method, not an exact tokenizer or provider billing integration.
- Imported pack commands may need follow-up adaptation after Q22 if direct import behavior or validation warnings are too broad for target repos.
- Q25 safe import scope is improved, but the imported `selftest`/`test` temp-fixture path still fails and remains a recorded handover limitation.
- First real implementation work should repair the target-local AIDE Lite `test`/`selftest` failure before broader Eureka-specific golden-task work.
