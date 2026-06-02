# PUBLIC-ALPHA-REASSESS-05 Runbook

Run the reassessment from committed examples only:

```powershell
python scripts/eureka_public_alpha_reassess.py --from-public-search-ux-projection-examples --json
python scripts/eureka_public_alpha_reassess_report.py --from-public-search-ux-examples --json
python scripts/eureka_public_alpha_route_smoke.py --from-examples --json
```

The expected decision is `launch_recommended: false`,
`demo_mode_recommended: true`, and `internal_review_recommended: true`.

Required checks:

- UX MVP implemented and verified from public-safe examples.
- 8 public UX routes and 8 result-card states are represented.
- No-JS and read-only projection flags remain true.
- Limited reviewed records remain distinct from verified artifacts.
- Reviewed corpus growth, external full discovery, main promotion, and launch
  approval remain future gates.

This runbook does not authorize deployment, publication, public launch,
site/dist writes, public index mutation, live source calls, downloads, file
fetches, OCR, extraction, install/execute behavior, or model/provider calls.
