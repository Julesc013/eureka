# Source Sync Job Flow

Future flow:

1. Approved source sync job is selected.
2. Source policy guard checks connector approval.
3. URI-R privacy guard validates approved source of URI.
4. User-Agent/contact, rate-limit, timeout, retry, and circuit-breaker config is checked.
5. Connector performs a bounded metadata-only request in future runtime.
6. Response is normalized to a capture/availability metadata summary.
7. Source-cache record candidate is validated.
8. Evidence-ledger observation candidate is built.
9. Candidate and evidence remain review-required.
10. No public index or master index mutation occurs.
11. Failures produce bounded error records, not raw payload dumps.

This flow is not implemented by P88.
