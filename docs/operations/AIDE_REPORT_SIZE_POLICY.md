# AIDE Report Size Policy

AIDE reports are repo control-plane artifacts. They support review, audit, and
handoff, but they do not define Eureka product behavior or production readiness.

Generated reports should remain small enough for ordinary Git review:

- warning threshold: 25 MB
- hard threshold: 50 MB
- preferred report target: 10 MB
- large generated reports should be represented as compact summaries plus
  deterministic shards

The report-size validator is:

```powershell
python scripts/validate_aide_report_sizes.py --json
```

The validator scans `.aide/reports`, `.aide/context`, `.aide/evals/runs`,
`.aide/changelog`, `.aide/quality`, and `.aide/repo`. It fails hard-threshold
files, opaque compressed report substitutes, missing file-quality ledger
replacement data, and raw prompt, raw response, or secret markers.

This policy does not allow product changes, source probes, extraction,
provider/model calls, deployment, production readiness claims, or public launch
claims.
