# Public Alpha Hosting Blockers

These blockers prevent real open-internet production exposure. They do not
prevent a short-lived, supervised public-alpha demo rehearsal when the runbook
checks pass and the operator can stop the process immediately.

## Blockers Before Real Public Hosting

- no auth or accounts
- no Eureka-provided HTTPS/TLS posture
- no rate limiting or abuse controls
- no production logging or monitoring posture
- no process supervisor or deployment posture
- local-path semantics still require careful mode policy
- review-required routes remain unresolved
- no public data governance policy
- no takedown or abuse contact process
- no production source-sync policy
- no privacy review for any future memory sharing
- no multi-user isolation model
- no durable public storage model
- no final public route contract

## Rehearsal Interpretation

For a supervised rehearsal, these blockers mean:

- keep the operator in the loop
- confirm `public_alpha` mode before exposing any route
- use the route inventory and smoke script as evidence
- stop immediately if any local path control succeeds in `public_alpha` mode
- do not claim production readiness

## Still Deferred

- deployment infrastructure
- auth and account design
- HTTPS/TLS ownership
- abuse controls
- production logging and monitoring
- source-sync policy
- public data governance
- route promotion or removal for `review_required` entries
