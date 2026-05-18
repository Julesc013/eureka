# Request Plan

The intended approved run is:

```powershell
python scripts/eureka_ia_live_metadata_probe.py --approve-live --query sampleproject --rows 1 --max-requests 2 --user-agent "EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)" --contact "local-operator" --json --redacted-output control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_redacted_summary.json --boundary-output control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_boundary_report.json
```

The first request is a one-row metadata search. A second exact item metadata
request is allowed only if the search returns a safe identifier and the request
cap is still available.
