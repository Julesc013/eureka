# Risks And Limitations

Remaining risks:

- validators are contract validators, not an import runtime
- checksum validation does not prove rights, safety, or truth
- public-safe classification still needs review for hosted/master use
- future staging roots must avoid leaking private local paths
- local-index-candidate mode could confuse claims with truth if not guarded
- contribution queue export could look like submission if naming is careless
- AI suggestions need separate provider and provenance governance
- import reports need their own stable format before tooling begins

This milestone intentionally leaves implementation deferred so these risks can
be handled before any local or hosted mutation is possible.

