# PUBLIC-ALPHA-REASSESS-03 Runbook

Run the reassessment from committed local-apply snapshot examples:

```bash
python scripts/eureka_public_alpha_reassess.py --from-local-apply-live-metadata-refresh-examples --json
python scripts/eureka_public_alpha_reassess_report.py --from-local-apply-live-metadata-examples --json
python scripts/eureka_public_alpha_route_smoke.py --from-examples --json
```

To regenerate examples, inventory, and audit evidence:

```bash
python scripts/eureka_public_alpha_reassess.py --from-local-apply-live-metadata-refresh-examples --write-examples --json
```

Use focused validation only. Do not run full unittest discovery inside the AI
session.

Required boundaries:

- No deployment or publication.
- No public launch or readiness claim.
- No public/master index mutation.
- No operator instance mutation.
- No live source calls.
- No downloads, extraction, execution, emulation, or model calls.
- No artifact verification, verified-download, malware-clean, or rights-clearance claims.
