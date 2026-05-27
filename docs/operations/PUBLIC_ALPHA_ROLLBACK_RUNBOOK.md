# Public Alpha Rollback Runbook

Rollback planning is required before any future public launch. This task records
the rollback model only; it does not deploy anything.

## Static Snapshot Site

1. Stop promotion of the new static artifact.
2. Restore the prior reviewed snapshot manifest.
3. Restore the prior relay manifest or generated relay data.
4. Re-run smoke checks against status, search, object, evidence, absence, and
   needs routes.

## Read-Only Relay Service

1. Pin the previous relay manifest.
2. Restart the read-only service with the previous manifest.
3. Verify no write routes, live source fanout, downloads, extraction, or model
   provider calls are enabled.

## Local Preview Server

Stop the preview process and discard preview-only environment variables. No
public state exists in this mode.

## Future Dynamic Gateway

Dynamic gateway hosting is blocked until a later reviewed task defines concrete
security, rate-limit, rollback, and incident procedures.
