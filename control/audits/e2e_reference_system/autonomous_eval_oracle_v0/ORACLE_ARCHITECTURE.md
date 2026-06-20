# Oracle Architecture

Implementation root:

```text
evals/e2e_reference/oracle/
```

Primary command:

```text
scripts/eureka_e2e_eval.py
```

Registry validator:

```text
tools/validators/validate_e2e_eval_oracle.py
```

Design:

```text
EvalCase registry
-> product adapter
-> observed artifacts
-> deterministic assertions
-> case result
-> suite gate
-> immutable eval report
```

The oracle creates isolated generated runs under `.eureka/e2e-reference/eval/`.
It never overwrites a previous execution ID.
