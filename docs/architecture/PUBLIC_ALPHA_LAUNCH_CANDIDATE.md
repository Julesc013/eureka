# Public Alpha Launch Candidate

`PUBLIC-ALPHA-LAUNCH-CANDIDATE-00` packages the promoted read-only public
alpha baseline for a future deploy dry-run decision. It is not a launch, not a
deployment, and not a production-readiness claim.

The candidate is limited to reviewed snapshot and relay projections:

- public routes and API routes are read-only
- public mutation is disabled
- no live source fanout is enabled
- public live source fanout is disabled
- downloads, uploads, extraction, and model/provider calls are disabled
- object, source, evidence, absence, and known-need packets are backed by the
  reviewed snapshot/relay foundation

The launch candidate can be marked ready only when prior promotion evidence,
focused validators, external full-discovery evidence, security planning,
privacy/abuse documentation, and rollback planning are present.

Any real deployment or public launch requires a future explicit task and manual
operator approval.
