# Public Alpha Reassess Runbook

Run the reassessment from committed examples:

```powershell
python scripts/eureka_public_alpha_reassess.py --from-snapshot-refresh-examples --json
python scripts/eureka_public_alpha_reassess_report.py --from-examples --json
python scripts/eureka_public_alpha_route_smoke.py --from-examples --json
```

To refresh public-safe reassessment examples:

```powershell
python scripts/eureka_public_alpha_reassess.py --from-snapshot-refresh-examples --write-examples --json
```

Validation:

```powershell
python scripts/validate_public_alpha_reassess.py
```

This runbook does not start a public server, does not deploy, and does not write
`site/dist` or `data/public_index`.
