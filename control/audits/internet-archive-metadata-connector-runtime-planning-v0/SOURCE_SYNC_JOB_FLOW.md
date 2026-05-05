# Source Sync Job Flow

Future flow:

1. Approved source sync job is selected.
2. Source policy guard checks connector approval.
3. User-Agent/contact, rate-limit, timeout, retry, and circuit-breaker config is checked.
4. Connector performs a bounded metadata-only request in future runtime.
5. Response is normalized to a metadata summary.
6. Source-cache record candidate is validated.
7. Evidence-ledger observation candidate is built.
8. Candidate and evidence remain review-required.
9. No public index or master index mutation occurs.
10. Failures produce bounded error records, not raw payload dumps.

This flow is not implemented by P87.
