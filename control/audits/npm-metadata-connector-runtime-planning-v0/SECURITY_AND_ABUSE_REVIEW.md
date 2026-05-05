# Security And Abuse Review

Required future controls: rate limits, timeout, circuit breaker, User-Agent/contact, token-free default, cache required before public use, kill switch, no public fanout, package identity guard, scoped package guard, dependency metadata guard, lifecycle-script guard, source policy guard, and operator approval. Monitoring is future-only.

Abuse cases: arbitrary package probing, private package leakage, private scope leakage, credentialed registry leakage, token forcing, tarball/package file download forcing, dependency resolution forcing, package install forcing, lifecycle script execution forcing, npm audit forcing, large version/dist-tag requests, retry storms, source blocking, and public query escalation.
