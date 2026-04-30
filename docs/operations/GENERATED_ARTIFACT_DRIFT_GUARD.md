# Generated Artifact Drift Guard

Generated Artifact Drift Guard v0 is a repo-local validation layer for committed
generated and generated-like artifacts. It records artifact ownership under
`control/inventory/generated_artifacts/` and checks that committed outputs still
match their current source inputs.

This guard is validation/audit only. It does not regenerate artifacts by
default, deploy, add runtime behavior, call external services, fetch URLs,
scrape, crawl, open sockets, or claim production readiness.
Static Artifact Promotion Review v0 now records `site/dist/` as conditionally
promoted for repo-local static publication while GitHub Actions deployment
status remains unverified.

## Covered Artifacts

- `site/dist/data/*.json`: generated public data summaries owned by
  `scripts/generate_public_data_summaries.py`.
- `site/dist/lite/`, `site/dist/text/`, and `site/dist/files/`: static
  compatibility surfaces owned by `scripts/generate_compatibility_surfaces.py`.
- `site/dist/demo/`: static resolver demo snapshots owned by
  `scripts/generate_static_resolver_demos.py`.
- `snapshots/examples/static_snapshot_v0/`: deterministic static snapshot seed
  example owned by `scripts/generate_static_snapshot.py`.
- `site/dist/`: canonical generated static deployment artifact owned by
  `site/build.py` and checked as `static_site_dist`.
- `tests/parity/golden/python_oracle/v0/`: Python oracle golden fixtures owned by
  `scripts/generate_python_oracle_golden.py`.
- `docs/operations/public_alpha_rehearsal_evidence_v0/`: public-alpha rehearsal
  evidence owned by `scripts/generate_public_alpha_rehearsal_evidence.py`.
- `control/inventory/publication/`: governed publication inventories validated by
  publication/static-site validators.
- `control/inventory/tests/`: governed test registry and command matrix metadata.
- `.aide/`: repo-operating command, queue, and report metadata.

## Checking Drift

Use:

```bash
python scripts/check_generated_artifact_drift.py
python scripts/check_generated_artifact_drift.py --json
python scripts/check_generated_artifact_drift.py --list
python scripts/check_generated_artifact_drift.py --artifact public_data_summaries
```

The checker reads `generated_artifacts.json` and `drift_policy.json`, verifies
declared artifact paths, resolves declared check commands, and runs the existing
owning checks. It records each artifact group as `passed`, `failed`, `skipped`,
or `unavailable`.

The default mode is deterministic and non-mutating. It runs check and validation
commands only. It never runs `update_command`.

## Refreshing Artifacts

When drift is detected, refresh only the affected artifact with its documented
`update_command`, then rerun the drift guard and the relevant validator lane.
Examples:

```bash
python scripts/generate_public_data_summaries.py --update
python scripts/generate_compatibility_surfaces.py --update
python scripts/generate_static_resolver_demos.py --update
python scripts/generate_static_snapshot.py --update
python scripts/generate_python_oracle_golden.py
python scripts/generate_public_alpha_rehearsal_evidence.py --update
```

Hybrid governance artifacts such as publication inventories, test registry
metadata, and AIDE metadata are hand-authored. They should be updated through
bounded governed edits and then validated with their declared check commands.

## Volatile Values

Known volatile fields are documented in the inventory. Owning generators must
normalize volatile values where deterministic checks depend on them, or the
field must be classified as volatile by its contract policy. Public data
stability classifications remain the guidance for generated public JSON.

## Cargo And External Tools

Cargo is optional for this guard. Generated Artifact Drift Guard v0 is a
Python/std-lib validation lane, and Cargo absence is not a drift failure unless
a future artifact group explicitly requires Cargo.

Network and deployment tools are out of scope. Commands declared for this guard
must stay repo-local and must not perform live probes, scraping, crawling,
external searches, URL fetching, or deployment.

## Remediation

When a check fails:

1. Read the failing artifact group in the JSON report.
2. Run the owning check command directly for detailed output.
3. Decide whether the source input changed intentionally.
4. If intentional, refresh the artifact with the documented update command or
   perform a governed metadata edit.
5. Rerun the drift guard, related validators, and `git diff --check`.

Do not hide drift by editing generated output without reviewing the owning
generator or source inputs.
