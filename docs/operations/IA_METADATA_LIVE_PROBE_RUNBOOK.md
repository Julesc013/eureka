# IA Metadata Live Probe Runbook

IA-02 is a local operator-approved metadata-only probe. It is not production,
public launch, source-cache, evidence, or reviewed-index readiness.

## Dry Run

```powershell
python scripts/eureka_ia_live_metadata_probe.py --dry-run --json
python scripts/validate_ia_live_metadata_probe.py
```

Dry-run mode builds a redacted request plan and performs no network access.

## Approved Probe

```powershell
python scripts/eureka_ia_live_metadata_probe.py --approve-live --query sampleproject --rows 1 --max-requests 2 --user-agent "EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)" --contact "local-operator" --json --redacted-output control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_redacted_summary.json --boundary-output control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_boundary_report.json
```

The probe may make at most two HTTP requests:

- one one-row metadata search
- one exact item metadata read if a safe identifier is returned

## Current IA-02 Outcome

The approved request was attempted once, but the local TLS trust store rejected
the certificate chain with `ssl_certificate_verify_failed`. This is recorded as
partial evidence, not success.

Do not bypass certificate verification to force a pass. Fix the local trust
environment or run the approved probe from a machine with a valid Python TLS
trust store.

## Boundaries

The live probe must not:

- commit raw live response bodies
- download files
- upload or call write APIs
- write source cache
- write evidence
- mutate candidate, reviewed, or master indexes
- run extraction
- call model/provider APIs
- deploy
- claim production or public launch readiness
