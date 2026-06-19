# Unknown Group Investigation

## Runtime Leakage

Classification: `genuine_product_regression`

The runtime leakage validator fails against the current repo. The validator
reports:

- gate status: `fail`
- new unallowlisted production-path findings: 52
- blocker findings: 36
- high findings: 16
- network calls made: false
- model provider calls made: false
- runtime modules imported by validator/audit: false

Representative new production-path findings:

- `runtime/local/staging_mvp.py`: `BUNDLE`, `MVP`
- `runtime/local/search_mvp.py`: `MVP`, `truth_boundary`
- `runtime/local/artifact_gate_seed.py`: `fixture_only`
- `runtime/local/external_staging_mvp.py`: `BUNDLE`
- `runtime/local/ia_candidate_review_batch.py`: `fixture_only`, `agent`
- `runtime/local/local_machine_public_exposure.py`: `BUNDLE`
- `runtime/local/public_alpha_mvp.py`: `MVP`
- `runtime/local/review_materialization.py`: `MVP`
- `runtime/local/search_index.py`: `MVP`
- `runtime/local/workbench_mvp.py`: `MVP`

The associated targeted test lane also fails:

```text
python -m unittest tests.operations.test_legacy_runtime_leakage_remediation tests.operations.test_runtime_architecture_leakage -v
```

Result:

```text
Ran 29 tests in 231.236s
FAILED (failures=2)
```

This task may not edit runtime product paths. The required next repair is a
separately authorized runtime leakage task.

Recommended task:

```text
SOURCE-FOUNDRY-RUNTIME-LEAKAGE-REPAIR-00
```

## Local Worker

Classification: `historical_queue_expectation_drift`

The local-worker validator fails in isolation, but the runtime behavior checks
pass. The failing validator errors are stale queue-state expectations:

```text
queue index must point to LOCAL-10
queue index must mark LOCAL-09 completed
queue index must include queued LOCAL-10
queue index must keep F0 deferred until LOCAL-14
```

The validator still expects the old `LOCAL-09` to `LOCAL-10` queue posture, while
the current queue is legitimately advanced to:

```text
REVIEW-IA-CANDIDATES-BATCH-00
```

Local-worker behavior remained intact:

- `noop_worker_passed`: true
- `review_queue_checker_passed`: true
- `absence_report_worker_passed`: true
- `local_status_snapshot_worker_passed`: true
- `reviewed_index_rebuild_worker_token_gated`: true
- blocked source/model/download/deployment workers remained blocked
- external network used: false
- production readiness claimed: false
- public launch readiness claimed: false

The associated targeted lane confirms the same single validator failure:

```text
python -m unittest tests.operations.test_local_worker_scripts -v
```

Result:

```text
Ran 3 tests in 123.957s
FAILED (failures=1)
```

This can be repaired as historical queue drift after the runtime leakage blocker
is handled or under a validator helper authority that allows the shared queue
progress helper.

