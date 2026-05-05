# Failure, Retry, Timeout, And Circuit-Breaker Plan

Future rules:

- timeout required
- max retries bounded
- exponential backoff or retry-after/abuse-limit respect
- per-source circuit breaker
- per-source rate limit
- no retry storms
- no public-search blocking
- no raw error payload leaks
- connector disabled on policy violation
- operator-visible failure summary
