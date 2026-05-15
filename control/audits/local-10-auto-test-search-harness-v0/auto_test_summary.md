# Auto-Test Summary

LOCAL-10 adds a deterministic localhost harness with these suites:

- service health
- JSON search
- HTML workbench
- absence semantics
- read-only safety
- worker queue safety
- latency smoke
- local state cleanliness

The harness refuses non-localhost base URLs and emits JSON plus Markdown
reports. It does not run source probes, extraction, model/provider calls, LAN,
deployment, downloads, installs, or execution.
