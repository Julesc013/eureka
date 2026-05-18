# Latest Task Packet

## TASK

IA-02-TLS-TRUST-CONTINUE - Repair local Python TLS trust and rerun approved IA
metadata probe.

## PHASE

IA-02 TLS trust continuation completed as `PASS`.

## GOAL

Repair or safely work around the local Python TLS trust configuration with TLS
verification enabled, rerun the approved bounded Internet Archive metadata-only
probe, and unblock IA-03 only after a successful verified HTTPS metadata
response exists.

## WHY

IA-02 previously failed before an IA HTTP response because the active Python
OpenSSL trust paths had no usable CA file/capath. IA-02-TLS-TRUST-01 diagnosed
that as a local trust-store issue. IA-03 could not proceed until verified TLS
and the approved IA metadata probe succeeded without weakening security.

## ALLOWED_PATHS

- IA live probe scripts and runtime under the approved IA-02 TLS continuation
  scope.
- TLS diagnostic and validator scripts.
- IA TLS/live-probe focused tests.
- IA TLS troubleshooting and live-probe docs.
- IA-02 TLS continuation inventories and audit pack.
- AIDE queue/context/report metadata for IA-02-TLS-TRUST-CONTINUE, IA-03, and
  SYN-00.

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files, credentials, raw prompts, raw responses, committed CA
  certificates, certificate bundles, and raw live IA response bodies
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

The diagnostic script now supports redacting local paths from committed
evidence. The TLS validator prefers the IA-02-TLS-TRUST-CONTINUE after-diagnosis
when present and still rejects insecure TLS bypass patterns.

The active Python environment has no top-level `certifi` and no default
OpenSSL CA file/capath, but it does have a pip-vendored CA bundle. Setting
`SSL_CERT_FILE` for the current shell only to that existing bundle allowed a
verified TLS handshake to `archive.org` with `CERT_REQUIRED` and hostname
checking enabled.

After that verified diagnostic passed, the approved IA metadata-only probe ran
with the IA-02 caps: query `sampleproject`, rows 1, max requests 2, explicit
User-Agent/contact. It succeeded with two HTTPS requests and wrote only redacted
summary, normalized preview, and boundary proof.

## EVIDENCE

- `control/inventory/ia_02_tls_continue_machine_diagnosis.json`
- `control/inventory/ia_02_tls_continue_operator_action.json`
- `control/inventory/ia_02_tls_continue_rerun_result_summary.json`
- `control/inventory/ia_02_tls_continue_normalized_preview.json`
- `control/inventory/ia_02_tls_continue_boundary_report.json`
- `control/inventory/ia_02_tls_continue_result.json`
- `control/audits/ia-02-tls-trust-continue-v0/`

## CONTEXT_REFS

- `control/inventory/ia_02_result.json`
- `control/inventory/ia_02_next_task_decision.json`
- `.aide/queue/IA-02-TLS-TRUST-CONTINUE/task.yaml`
- `.aide/queue/IA-03/task.yaml`
- `.aide/queue/index.yaml`
- `docs/operations/IA_TLS_TRUST_TROUBLESHOOTING.md`
- `docs/operations/IA_METADATA_LIVE_PROBE_RUNBOOK.md`

## VALIDATION

Required focused validation passed:

- IA metadata policy validator
- IA fixture replay validator
- IA live-probe dry-run
- Python TLS diagnostic after current-shell CA setting
- IA TLS trust validator
- IA live-probe validator
- IA TLS/live-probe focused unittest modules
- architecture boundary and generated artifact cleanliness checks

## NON_GOALS

- No TLS verification disabling.
- No insecure context, `verify=False`, or hostname-check bypass.
- No committed CA certificate, certificate bundle, or machine-specific path.
- No raw IA response body commit.
- No broad retry loop.
- No downloads/uploads.
- No source-cache, evidence, candidate, reviewed, or master-index mutation.
- No extraction, model/provider calls, deployment, production readiness claim,
  or public launch claim.

## ACCEPTANCE

Status is `PASS`.

- TLS before/after diagnostics are recorded with local paths redacted.
- TLS verification remained enabled.
- The safe action class is `valid_ca_bundle_env_needed_for_current_shell`.
- Approved live probe rerun succeeded.
- Redacted summary, normalized preview, and boundary report exist.
- IA-03 is unblocked for source-cache write path planning.

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

Approximate task packet tokens: 950.
