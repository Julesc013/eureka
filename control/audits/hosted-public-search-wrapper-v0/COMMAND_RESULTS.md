# Command Results

| Command | Status | Notes |
| --- | --- | --- |
| `git status --short --branch` | pass | Initial P54 status was clean on `main...origin/main`. |
| `git rev-parse HEAD` | pass | Initial head `40db3221e2c470489e60aebf2821001c820238e9`. |
| `git rev-parse origin/main` | pass | Initial origin/main matched head. |
| `git log --oneline -n 50` | pass | P50 through P53 commits were present. |
| `python scripts/run_hosted_public_search.py --check-config` | pass | Safe defaults accepted. |
| `python scripts/run_hosted_public_search.py --check-config --json` | pass | JSON parsed and reported `status: valid`. |
| `python scripts/check_hosted_public_search_wrapper.py` | pass | Local rehearsal passed 14/14 checks. |
| `python scripts/check_hosted_public_search_wrapper.py --json` | pass | JSON rehearsal passed 14/14 checks. |
| `EUREKA_ALLOW_LIVE_PROBES=1 python scripts/run_hosted_public_search.py --check-config` | pass_expected_failure | Refused prohibited live probes. |
| `EUREKA_ALLOW_DOWNLOADS=1 python scripts/run_hosted_public_search.py --check-config` | pass_expected_failure | Refused prohibited downloads. |
| `EUREKA_ALLOW_UPLOADS=1 python scripts/run_hosted_public_search.py --check-config` | pass_expected_failure | Refused prohibited uploads. |
| `EUREKA_ALLOW_LOCAL_PATHS=1 python scripts/run_hosted_public_search.py --check-config` | pass_expected_failure | Refused prohibited local path access. |
| `python scripts/validate_hosted_public_search_wrapper.py` | pass | P54 audit pack, wrapper, docs, inventory, and hard false booleans validated. |
| `python scripts/validate_hosted_public_search_wrapper.py --json` | pass | JSON validator output parsed with `status: valid`. |
| `python -m unittest discover -s tests/scripts -t .` | pass_after_repair | Initial run exposed stale static-host Dockerfile guard; after narrow P54 Dockerfile allowance, 235 tests passed. |
| `python -m unittest discover -s tests/operations -t .` | pass_after_repair | Initial run exposed stale GitHub Pages provider-config guard; after safe-wrapper Dockerfile check, 414 tests passed. |
| `python -m unittest discover -s tests/hardening -t .` | pass | 53 tests passed. |
| `python -m unittest discover -s tests/parity -t .` | pass | 25 tests passed. |
| `python -m unittest discover -s runtime -t .` | pass | 320 tests passed. |
| `python -m unittest discover -s surfaces -t .` | pass | 168 tests passed. |
| `python -m unittest discover -s tests -t .` | pass | 818 tests passed. |
| Public search contract, result-card, safety, and local runtime validators, including JSON variants | pass | Public search stayed `local_index_only`; hosted search and unsafe behavior remain unclaimed. |
| `python scripts/public_search_smoke.py` and `--json` | pass | Passed 30/30 checks. |
| `python scripts/public_alpha_smoke.py` | pass | Passed 18/18 checks. |
| P53/P52/P51/P50 validators | pass | Production contract, static deployment evidence, post-P50 remediation, and post-P49 audit validators passed. |
| Static generation/publication validators | pass | `site/build.py --check`, `site/build.py --json`, `site/validate.py`, `site/validate.py --json`, publication inventory, public static site, Pages artifact, and generated drift checks passed sequentially. |
| `python scripts/run_archive_resolution_evals.py` and `--json` | pass | Archive resolution evals stayed satisfied: 6/6. |
| `python scripts/run_search_usefulness_audit.py` and `--json` | pass | Counts: covered=5, partial=40, source_gap=10, capability_gap=7, unknown=2, total=64. |
| `python scripts/report_external_baseline_status.py --json` | pass | External baselines remain manual/pending: 192 pending, 0 observed; batch_0 39 pending, 0 observed. |
| `python scripts/generate_python_oracle_golden.py --check` | pass | Python oracle golden fixture pack remained current. |
| `python scripts/check_architecture_boundaries.py` | pass | Architecture boundary checks passed. |
| Live-backend and static-host readiness validators, including JSON variants | pass_after_repair | Both now allow only the safe P54 wrapper Dockerfile while preserving no-hosted-deployment and no-provider-config guards. |
| `cargo --version` | unavailable | Cargo is not installed in this environment. |
| `cargo check --workspace --manifest-path crates/Cargo.toml` | unavailable | Cargo is not installed in this environment. |
| `cargo test --workspace --manifest-path crates/Cargo.toml` | unavailable | Cargo is not installed in this environment. |

Two transient/local blockers were repaired during verification: the old static
host and GitHub Pages checks treated the new safe P54 wrapper Dockerfile as a
generic provider config. The repair is intentionally narrow: the Dockerfile is
accepted only when it runs `scripts/run_hosted_public_search.py` with the safe
`local_index_only` env defaults and no secret-like settings.
