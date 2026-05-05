# Source Sync Job Flow

1. Approved source sync job is selected.
2. Source policy guard checks connector approval.
3. SWHID/origin/repository identity guard validates approved identity source.
4. Source-code-content risk guard verifies metadata-only handling.
5. Token/auth guard verifies v0 is token-free unless future policy approves otherwise.
6. User-Agent/contact/rate-limit/timeout/circuit-breaker config is checked.
7. Connector performs bounded metadata-only request in future runtime.
8. Response is normalized to SWHID/origin/visit/snapshot/release/revision metadata summary.
9. Source cache record candidate is validated.
10. Evidence ledger observation candidate is built.
11. Candidate/evidence remains review-required.
12. No public index/master index mutation occurs.
13. Failures produce bounded error records, not raw payload dumps.
