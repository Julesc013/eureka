# Track B Gap Register

## Critical Blockers

- None found in the Track B local foundry spine.

## Warnings

- Active merge with unrelated staged Track B and OBS changes.
- Full unittest failure in OBS hardening guard outside the Track B spine.
- Evidence ledger contract material is documented under reference docs and
  inventories rather than `contracts/evidence/`.
- B22 commit was blocked by the active merge.

## Deferred IA Connector Prerequisites

- Source policy approval for Internet Archive metadata.
- User-Agent and contact posture decision.
- Rate-limit, quota, and cache TTL policy.
- Kill switch and failure-mode policy.
- Explicit approval before any external call.

## Deferred Track Dependencies

- Track C: native clients remain deferred.
- Track D: snapshot and relay behavior remain deferred.
- Track E: hosted operations and telemetry posture remain deferred.
- Later track: actual public-index rebuild, pack import, pack submission,
  hosted upload, and federation remain deferred.

## Optional Track B Follow-Ups

- Consider adding `contracts/evidence/` only if future governance wants schema
  files in that family.
- Resolve the active merge and OBS hardening strings before claiming a clean
  full-suite result.
