# Latest Task Packet

## TASK

IA-02-TLS-TRUST-01 - Diagnose local Python TLS trust and rerun approved IA
metadata probe.

## PHASE

IA-02 TLS trust follow-up completed as `PASS_WITH_WARNINGS`.

## GOAL

Diagnose the local Python TLS trust failure, preserve verified TLS, rerun the
approved bounded IA metadata probe only if safe, and keep IA-03 blocked until a
successful verified HTTPS metadata response exists.

## WHY

IA-02 reached the approved live metadata probe but failed before an Internet
Archive HTTP response because the local Python TLS verifier could not build a
trusted chain. The follow-up must diagnose that environment problem without
weakening TLS, and IA-03 must remain blocked until a successful verified HTTPS
metadata response exists.

## ALLOWED_PATHS

- `runtime/source_observation/internet_archive_live_transport.py`
- `runtime/source_observation/internet_archive_live_probe.py`
- `runtime/source_observation/internet_archive_validation.py`
- `scripts/diagnose_python_tls_trust.py`
- `scripts/validate_ia_tls_trust.py`
- `scripts/eureka_ia_live_metadata_probe.py`
- `scripts/validate_ia_live_metadata_probe.py`
- `docs/operations/IA_TLS_TRUST_TROUBLESHOOTING.md`
- `docs/operations/IA_METADATA_LIVE_PROBE_RUNBOOK.md`
- `docs/reference/IA_METADATA_LIVE_PROBE.md`
- IA-02 TLS inventories and audit pack under `control/inventory/` and
  `control/audits/ia-02-tls-trust-01-v0/`
- AIDE queue/context/report metadata for this task and IA-03 gating.

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files, credentials, raw prompts, and raw responses
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

Added a verified Python TLS diagnostic and an IA TLS validator. The diagnostic
uses `ssl.create_default_context()` with hostname checking enabled, reports
default verify paths, certificate-related environment variables, DNS status,
and a redacted verified TLS handshake result. The validator rejects insecure TLS
bypass patterns and confirms IA-03 remains blocked when the local trust chain
still fails.

No approved IA live probe rerun was performed because the verified TLS
diagnostic still fails locally.

## EVIDENCE

- `control/inventory/ia_02_tls_trust_diagnosis.json`
- `control/inventory/ia_02_tls_trust_repair_decision.json`
- `control/inventory/ia_02_tls_trust_result.json`
- `control/inventory/ia_02_tls_next_task_decision.json`
- `control/audits/ia-02-tls-trust-01-v0/`
- `docs/operations/IA_TLS_TRUST_TROUBLESHOOTING.md`
- `tests/operations/test_ia_tls_trust_diagnostics.py`

## CONTEXT_REFS

- `control/inventory/ia_02_result.json`
- `control/inventory/ia_02_tls_trust_diagnosis.json`
- `control/inventory/ia_02_tls_trust_repair_decision.json`
- `control/inventory/ia_02_tls_trust_result.json`
- `control/inventory/ia_02_tls_next_task_decision.json`
- `control/audits/ia-02-tls-trust-01-v0/`
- `.aide/queue/IA-02-TLS-TRUST-01/task.yaml`
- `.aide/queue/IA-03/task.yaml`

## VALIDATION

Passing focused validation:

- `python scripts/validate_ia_metadata_policy.py`
- `python scripts/validate_ia_fixture_replay.py`
- `python scripts/eureka_ia_live_metadata_probe.py --dry-run --json`
- `python scripts/diagnose_python_tls_trust.py --host archive.org --json`
- `python scripts/validate_ia_tls_trust.py`
- `python scripts/validate_ia_live_metadata_probe.py`
- IA live-probe and TLS focused unittest modules
- `python scripts/check_architecture_boundaries.py`

Expected pre-commit generated-artifact cleanliness warning:

- new audit generated evidence is untracked until commit.

## NON_GOALS

- No TLS verification disabling.
- No `ssl._create_unverified_context`.
- No `verify=False` equivalent.
- No hostname-check bypass.
- No custom insecure CA bundle.
- No raw response commit.
- No broad retry loop.
- No downloads/uploads.
- No source-cache, evidence, candidate, reviewed, or master-index mutation.
- No extraction, model/provider calls, deployment, production readiness claim,
  or public launch claim.

## ACCEPTANCE

Status is `PASS_WITH_WARNINGS`.

- TLS diagnostic exists and runs.
- TLS validator exists and passes.
- TLS verification remains enabled.
- No insecure TLS bypass is used.
- Issue is classified as `local_python_trust_store`.
- Operator machine action is required.
- Live probe rerun was not attempted.
- IA-03 remains blocked until a successful approved HTTPS metadata response
  exists.

## OUTPUT_SCHEMA

Final response sections:

- `STATUS`
- `SUMMARY`
- `COMMITS`
- `TLS`
- `IA_RERUN`
- `VALIDATION`
- `BOUNDARIES`
- `NEXT_TASK`

## TOKEN_ESTIMATE

Approximate task packet tokens: 850.
