# Implementation Phases

Phase 0: keep disabled.

- Complete planning and validation.

Phase 1: local dry-run normalizer over synthetic fixtures only.

- No network.

Phase 2: local approved live metadata probe only after human/operator approval.

- Strict SWHID/origin/repository identity, User-Agent/contact, rate-limit, timeout, and cache gates.
- Token-free unless future explicit approval.
- No public search fanout.
- No content/blob/directory/source-code/source-archive/repository clone operations.

Phase 3: source sync worker integration writes source-cache/evidence-ledger candidates.

- Still no master/public index mutation.

Phase 4: public index rebuild from reviewed cache/evidence.

- Still no public live fanout.

Phase 5: hosted connector worker with monitoring, rollback, quotas, and operator kill switch.
