# HTML Workbench Summary

LOCAL-05 adds `surfaces/web/workbench/local_html` as a deterministic server-rendered HTML layer for the local appliance.

Pages:

- home and search
- object detail
- source records
- local absence
- status

The workbench uses presentation-safe view models and renders through `runtime/local_service`; it does not open store paths directly.
