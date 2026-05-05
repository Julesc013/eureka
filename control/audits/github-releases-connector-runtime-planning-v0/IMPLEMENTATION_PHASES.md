# Implementation Phases

Phase 0: keep disabled and complete planning and validation.

Phase 1: local dry-run normalizer over synthetic fixtures only, with no network.

Phase 2: local approved live metadata probe only after human/operator approval, strict repository identity/User-Agent/contact/rate-limit/timeout/cache controls, token-free unless future explicit approval, no public search fanout, and no release asset or source archive fetch.

Phase 3: source sync worker integration writes source-cache and evidence-ledger candidates, still with no master or public index mutation.

Phase 4: public index rebuild from reviewed cache/evidence, still with no public live fanout.

Phase 5: hosted connector worker with monitoring, rollback, quotas, and operator kill switch.
