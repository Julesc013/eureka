# Post Public Alpha Read-Only Closeout Plan

External full discovery has passed outside the AI session. The next step is
`DEV-TO-MAIN-PROMOTION-REVIEW-04`.

Preferred background run:

```powershell
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --background --clean
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --handoff
```

## External Full Discovery Result

```text
status: pass
tests_run: 5050
failures: 0
errors: 0
exit_code: 0
```

Deployment and public launch claims remain false.

## If External Full Discovery Fails

1. Classify the compact failure families.
2. Repair only in-scope failures.
3. Rerun focused tests.
4. Request another external full-discovery run only if needed.

Do not start promotion, deployment, live source fanout, public mutation,
downloads, extraction, model/provider calls, native work, or launch-candidate
work from this waiting state. There is no deployment approval and no public
launch readiness claim in this closeout state.
