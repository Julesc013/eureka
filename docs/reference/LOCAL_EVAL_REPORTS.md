# Local Eval Reports

The local eval harness emits JSON and Markdown summaries.

## JSON Report

Schema: `local_eval_report.v0`

The report includes:

- overall status
- suite status
- per-case status
- per-route elapsed milliseconds
- warnings and limitations
- boundary flags for network, source probes, extraction, model providers, LAN,
  deployment, `site/dist`, and master-index mutation

All boundary flags must remain false for LOCAL-10.

## Markdown Summary

`scripts/eureka_local_eval_report.py` converts a JSON report into a short
Markdown summary. The conversion is read-only except for the explicit output
path supplied by the operator.
