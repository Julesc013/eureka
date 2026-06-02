# PUBLIC-ALPHA-REASSESS-04 Runbook

Run from clean `dev`.

```powershell
python scripts/eureka_public_alpha_reassess.py --from-manuals-driver-snapshot-examples --json
python scripts/eureka_public_alpha_reassess_report.py --from-manuals-driver-examples --json
python scripts/eureka_public_alpha_route_smoke.py --from-examples --json
python scripts/validate_public_alpha_reassess.py
```

The reassessment must not deploy, publish, mutate public indexes, fetch files,
run OCR, execute installers, call models, or claim production or public-launch
readiness.

Expected decision:

- `launch_recommended: false`
- `demo_mode_recommended: true`
- `internal_review_recommended: true`
- `public_search_ux_mvp_implemented: false`
- `needs_public_search_ux_mvp: true`
- next task: `PUBLIC-SEARCH-UX-MVP-00`

Full unittest discovery remains outside this AI-assisted lane.
