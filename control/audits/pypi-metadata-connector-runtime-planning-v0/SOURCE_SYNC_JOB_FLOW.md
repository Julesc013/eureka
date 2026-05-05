# Source Sync Job Flow

Future flow:

1. Approved source sync job is selected.
2. Source policy guard checks connector approval.
3. Package identity guard validates approved package-name source.
4. Dependency metadata caution guard verifies metadata-only handling.
5. Token/auth guard verifies v0 is token-free unless future policy approves otherwise.
6. User-Agent/contact/rate-limit/timeout/circuit-breaker config is checked.
7. Connector performs bounded metadata-only request in future runtime.
8. Response is normalized to project/release/file metadata summary.
9. Source cache record candidate is validated.
10. Evidence ledger observation candidate is built.
11. Candidate/evidence remains review-required.
12. No public index or master index mutation occurs.
13. Failures produce bounded error records, not raw payload dumps.
