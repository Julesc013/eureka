# Dev To Main Promotion Review 05

`DEV-TO-MAIN-PROMOTION-REVIEW-05` promotes the public alpha launch-candidate and
deploy dry-run evidence only after current external full discovery passes.

Current state is waiting:

- `origin/main` can fast-forward to `origin/dev`
- deploy dry-run evidence passes
- launch-candidate evidence passes
- no deployment or public launch occurred
- no production or public launch readiness claim is made
- external full discovery for current `dev` head is still required

Run the external gate outside AI:

```powershell
python scripts/eureka_test_gate.py --gate promotion_gate --watch --clean
```

Do not promote `main` until a passing compact handoff is returned.
