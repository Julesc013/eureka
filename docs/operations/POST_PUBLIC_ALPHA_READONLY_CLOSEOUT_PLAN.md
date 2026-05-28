# Post Public Alpha Read-Only Closeout Plan

The next step is external full discovery outside the AI session.

Preferred background run:

```powershell
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --background --clean
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --handoff
```

## If External Full Discovery Passes

1. Validate the compact summary with `scripts/validate_test_run_summary.py`.
2. Update the closeout result to `pass`.
3. Keep deployment and public launch claims false.
4. Proceed to `DEV-TO-MAIN-PROMOTION-REVIEW-04`.

## If External Full Discovery Fails

1. Classify the compact failure families.
2. Repair only in-scope failures.
3. Rerun focused tests.
4. Request another external full-discovery run only if needed.

Do not start promotion, deployment, live source fanout, public mutation,
downloads, extraction, model/provider calls, native work, or launch-candidate
work from this waiting state. There is no deployment approval and no public
launch readiness claim in this closeout state.
