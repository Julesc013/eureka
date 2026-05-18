# IA TLS Trust Troubleshooting

IA metadata probes must use normal TLS certificate verification. Do not disable
verification, use `ssl._create_unverified_context`, turn off hostname checking,
or add a `verify=False` equivalent.

## Diagnose

```powershell
python scripts/diagnose_python_tls_trust.py --host archive.org --json
python scripts/validate_ia_tls_trust.py
```

The diagnostic reports:

- Python executable and version
- OpenSSL version
- default verify paths
- certificate-related environment variables
- whether `certifi` is available
- DNS resolution
- a verified TLS handshake result

It performs a TLS handshake only. It does not fetch IA item files, media,
metadata documents, or download content.

## Current Finding

On this machine, Python 3.11 can create a verified default context and resolve
`archive.org`, but the verified handshake fails:

```text
ssl_certificate_verify_failed / self_signed_certificate_in_chain
```

The OpenSSL default CA file and CA directory paths do not exist, and `certifi`
is not available. That means the failure is local Python trust configuration,
possibly combined with local network TLS inspection.

IA-02-TLS-TRUST-CONTINUE confirmed that this Python install has an existing
pip-vendored CA bundle. Setting `SSL_CERT_FILE` to that bundle for the current
operator shell only allowed the verified handshake to pass. The local path is
machine-specific and must not be committed.

## Safe Local Repair Options

Operator actions may include:

- install or repair the Python certificate bundle for this Python installation
- configure `SSL_CERT_FILE` or `SSL_CERT_DIR` to a trusted local CA bundle
- install `certifi` and configure Python/OpenSSL to use a valid CA bundle
- if a corporate/security appliance performs TLS inspection, install its root
  CA into the Python-trusted bundle through normal operating-system or Python
  certificate management

Do not commit local CA bundles, private certificates, proxy credentials, or
machine-specific trust-store files to the repo.

## Rerun

Only rerun the approved IA probe after the diagnostic reports
`tls_handshake_status: pass`:

```powershell
$env:SSL_CERT_FILE = python -c "import pip._vendor.certifi as certifi; print(certifi.where())"
python scripts/diagnose_python_tls_trust.py --host archive.org --json
python scripts/eureka_ia_live_metadata_probe.py --approve-live --query sampleproject --rows 1 --max-requests 2 --user-agent "EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)" --contact "local-operator" --json --redacted-output control/audits/ia-02-tls-trust-continue-v0/generated/live_probe_redacted_summary.json --boundary-output control/audits/ia-02-tls-trust-continue-v0/generated/live_probe_boundary_report.json
```

IA-03 remains blocked until a successful approved HTTPS metadata response,
redacted summary, normalized preview, and boundary report exist. IA-02-TLS-
TRUST-CONTINUE produced that evidence; IA-03 may now define the source-cache
write path, while source-cache writes remain forbidden until that task.
