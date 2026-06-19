# E2E Reference Runner Runbook

The E2E reference runner is the local, headless orchestration spine for the
reference-system track.

## Synthetic Run

```text
python scripts/eureka_resolution_run.py run --mode synthetic --query "old blue FTP client for XP" --out .eureka/e2e-reference/runs
```

The command writes a generated local run bundle under:

```text
.eureka/e2e-reference/runs/<run-id>/
```

Generated `.eureka/` output is local/private state and is not committed.

## Validate A Bundle

```text
python scripts/eureka_resolution_run.py validate --run-dir .eureka/e2e-reference/runs/<run-id> --strict
```

Strict validation checks manifest files, file hashes, event sequence, payload
hashes, and the event hash chain.

## Replay A Bundle

```text
python scripts/eureka_resolution_run.py replay --run-dir .eureka/e2e-reference/runs/<run-id> --strict
```

Replay performs no provider call and creates no accepted truth. It writes
`replay_report.json` into the generated bundle.

## Status And Events

```text
python scripts/eureka_resolution_run.py status --run-dir .eureka/e2e-reference/runs/<run-id>
python scripts/eureka_resolution_run.py events --run-dir .eureka/e2e-reference/runs/<run-id>
```

## Blocked Live-Shadow Probe

```text
python scripts/eureka_resolution_run.py run --mode live-shadow --query "old blue FTP client for XP"
```

The command exits nonzero with an explicit `policy_blocked` result. It must not
call a provider or network.

## Legacy Compatibility

The previous dry-run command remains supported:

```text
python scripts/eureka_resolution_run.py --query sampleproject --projection operator_workbench --json
```

That path now delegates through the shared runner compatibility facade while
preserving the existing result keys.

## Safety Invariants

- no reviewed-record creation;
- no review-ledger decision write;
- no reviewed/master/public index mutation;
- no snapshot publication;
- no provider/network call in synthetic or replay;
- no downloads, uploads, extraction, execution, or model calls;
- no public exposure;
- no license posture change.
