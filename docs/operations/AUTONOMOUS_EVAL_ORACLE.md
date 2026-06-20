# Autonomous Eval Oracle Operations

List suites and cases:

```powershell
python scripts/eureka_e2e_eval.py list --json
```

Explain a case:

```powershell
python scripts/eureka_e2e_eval.py explain --case boundary_privacy_canaries --json
```

Run the core suite:

```powershell
python scripts/eureka_e2e_eval.py run --suite core --out .eureka/e2e-reference/eval --json
```

Run the offline all suite:

```powershell
python scripts/eureka_e2e_eval.py run --suite all --out .eureka/e2e-reference/eval --json
```

Run one case:

```powershell
python scripts/eureka_e2e_eval.py run --case metamorphic_equivalent_blue_ftp --out .eureka/e2e-reference/eval --json
```

Validate a generated run:

```powershell
python scripts/eureka_e2e_eval.py validate --run-dir .eureka/e2e-reference/eval/<execution-id> --strict --json
```

Check status:

```powershell
python scripts/eureka_e2e_eval.py status --run-dir .eureka/e2e-reference/eval/<execution-id> --json
```

Compare a run with the tracked baseline:

```powershell
python scripts/eureka_e2e_eval.py compare --left evals/e2e_reference/oracle/baselines/reference_v0.json --right .eureka/e2e-reference/eval/<execution-id> --json
```

Validate the registry:

```powershell
python tools/validators/validate_e2e_eval_oracle.py --json
```

## Interpreting Results

`PASS` means every critical and required case passed and no advisory warning
was emitted. `PASS_WITH_WARNINGS` means critical and required cases passed but
advisory resource or diagnostic cases warned. `FAIL` means a critical or
required invariant failed. `BLOCKED` means a required or critical case could
not be evaluated.

The oracle complements focused tests and full discovery. It does not replace
full unittest discovery, public launch gates, production readiness review, or
human acceptance.

Generated runs under `.eureka/` are local artifacts and are not committed.
