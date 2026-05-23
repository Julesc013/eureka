# AIDE Ledger Size v1

## Summary

`.aide/` remains allowed as repo operating metadata, but it is explicitly not
product truth. Export, generated, cache, report, repo-map, root-classification,
and tool-inventory areas are classified and retention-capped.

## Current Counts

- `.aide/` tracked files: `1990`
- `.aide/export`: `620`
- `.aide/reports`: `47`
- `.aide/repo`: `15`
- `.aide/roots`: `9`
- `.aide/tools`: `22`

## Policy

See `control/policies/aide_ledger_size_policy.json`.

## Non-Claims

- AIDE generated/export/report state is not product behavior.
- AIDE Lite does not own source truth.
- No provider, model, or network calls are enabled.
