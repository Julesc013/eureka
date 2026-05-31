# Public Alpha Reassess 01 Runbook

Run the reassessment from committed live-metadata refresh examples:

```powershell
python scripts/eureka_public_alpha_reassess.py --from-live-metadata-refresh-examples --json
python scripts/eureka_public_alpha_reassess_report.py --from-live-metadata-examples --json
python scripts/eureka_public_alpha_route_smoke.py --from-examples --json
```

Refresh public-safe reassessment examples:

```powershell
python scripts/eureka_public_alpha_reassess.py --from-live-metadata-refresh-examples --write-examples --json
```

Validate the reassessment lane:

```powershell
python scripts/validate_public_alpha_reassess.py
```

This runbook uses committed examples and redacted summaries only. It does not
start a server, call live sources, deploy, write `site/dist`, mutate indexes, or
promote candidates.

