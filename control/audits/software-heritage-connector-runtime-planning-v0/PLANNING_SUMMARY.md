# Planning Summary

P92 evaluates whether Eureka is ready for a bounded, software-archive-identity-and-metadata-only, cache-first Software Heritage connector runtime.

Decision: `blocked_connector_approval_pending`. The minimal future runtime path is documented, but implementation remains blocked until connector approval, SWHID/origin/repository identity review, source-code-content risk policy, token/auth policy, Software Heritage API/source policy, User-Agent/contact, rate-limit/timeout/retry/circuit-breaker values, and cache/evidence runtime gates are complete.

The future connector would only summarize approved metadata into source-cache candidates and evidence-ledger observation candidates. It would not invent object truth, mutate the master index, or provide public-query live fanout.
