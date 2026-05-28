# Root Tests

`tests/` is reserved for verification that crosses component boundaries or
protects repo-wide operating discipline.

Current families:

- `architecture/`: architecture boundary guards and synthetic violations.
- `evals/`: repo-level validation for benchmark/eval assets.
- `hardening/`: high-risk guards for eval truth, path safety, route/docs drift,
  parity/golden discipline, and repo metadata consistency.
- `integration/`: cross-component checks across contracts, runtime, and
  surfaces.
- `operations/`: repo-operating checks for public-alpha posture, audit packs,
  launch gates, and validation matrices.
- `scripts/`: stable `scripts/` wrapper checks.
- `tools/`: implementation-level checks for tooling under `tools/`.
- `parity/`: Python-oracle to Rust-candidate parity checks and plans.
- `end_to_end/`: higher-level workflow checks.

Component-local tests stay with their owning component. Full unittest discovery
must run outside AI chat/model sessions through the harness or CI when required:

```powershell
python scripts/run_full_unittest_discovery.py --out ..\eureka-test-runs\manual_full_discovery
```
