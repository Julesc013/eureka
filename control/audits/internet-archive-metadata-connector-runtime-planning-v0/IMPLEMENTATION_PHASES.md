# Implementation Phases

Phase 0: keep disabled; complete planning and validation.

Phase 1: local dry-run normalizer over synthetic fixtures only; no network.

Phase 2: local approved live metadata probe only after human/operator approval, strict User-Agent/contact, rate-limit, timeout, cache, and no public search fanout.

Phase 3: source sync worker integration writes source-cache and evidence-ledger candidates; still no master/public index mutation.

Phase 4: public index rebuild from reviewed cache/evidence; still no public live fanout.

Phase 5: hosted connector worker with monitoring, rollback, quotas, and operator kill switch.
