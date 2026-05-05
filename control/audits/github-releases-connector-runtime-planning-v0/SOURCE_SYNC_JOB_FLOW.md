# Source Sync Job Flow

Future flow:

1. Approved source sync job is selected.
2. Source policy guard checks connector approval.
3. Repository identity guard validates approved owner/repo source.
4. Token/auth guard verifies v0 is token-free unless future policy approves otherwise.
5. User-Agent/contact/rate-limit/timeout/circuit-breaker config is checked.
6. Connector performs bounded metadata-only request in future runtime.
7. Response is normalized to release/tag/asset metadata summary.
8. Source cache record candidate is validated.
9. Evidence ledger observation candidate is built.
10. Candidate/evidence remains review-required.
11. No public index or master index mutation occurs.
12. Failures produce bounded error records, not raw payload dumps.
