# Public Search Rollback

Status: operator procedure placeholder; no hosted deployment exists.

P54 adds the hosted wrapper but does not create a running service. Rollback
therefore remains an operator procedure to apply during a later hosted
rehearsal or public alpha.

Rollback checks must preserve `local_index_only`, no live probes, no downloads,
no uploads, no accounts, no telemetry, and no arbitrary URL fetch.

## Minimum Future Procedure

1. Keep the previous deployed commit or image digest available.
2. Keep safe environment variables versioned outside secrets.
3. Confirm `EUREKA_OPERATOR_KILL_SWITCH=1` stops startup during emergency
   rollback.
4. Revert to the previous service revision or image.
5. Check `/healthz`.
6. Check `/api/v1/status`.
7. Verify unsafe parameters are still rejected.
8. Record rollback time, commit, operator, and route evidence.

## Current Repo Posture

- No provider service is configured as active.
- No DNS or TLS change is performed.
- No database, object store, worker plane, queue, account system, telemetry
  runtime, live connector, or AI provider is attached.
- No rollback has been exercised against a hosted provider.

The next hosted rehearsal milestone must turn this checklist into evidence.
## P58 Rehearsal Rollback Status

P58 performs no deployment, so there is no hosted rollback event. The local
rehearsal starts a localhost wrapper process and terminates it after route and
safety checks. Real rollback evidence remains operator-gated for a future
hosted deployment.
## P64 Candidate Index Note

There is no P64 runtime candidate index to roll back. If a future milestone
adds candidate runtime behavior, rollback must include candidate-store disable,
public-search injection disable, promotion disable, and source/evidence write
disable checks before operator use.
