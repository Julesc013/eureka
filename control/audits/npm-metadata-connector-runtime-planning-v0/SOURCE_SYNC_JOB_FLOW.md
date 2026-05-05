# Source Sync Job Flow

1. Approved source sync job is selected.
2. Source policy guard checks connector approval.
3. Package identity guard validates approved package-name source.
4. Scoped package guard verifies scope handling and rejects private or credentialed scopes.
5. Dependency metadata caution guard verifies metadata-only handling.
6. Lifecycle-script risk guard verifies no script execution and no script-safety claim.
7. Token/auth guard verifies v0 is token-free unless future policy approves otherwise.
8. User-Agent/contact/rate-limit/timeout/circuit-breaker config is checked.
9. Connector performs bounded metadata-only request in future runtime.
10. Response is normalized to package/version/dist-tag/tarball metadata summary.
11. Source cache record candidate is validated.
12. Evidence ledger observation candidate is built.
13. Candidate/evidence remains review-required.
14. No public index/master index mutation occurs.
15. Failures produce bounded error records, not raw payload dumps.
