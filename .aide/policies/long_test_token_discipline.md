# Long Test Token Discipline

- AI agents must not babysit long-running test commands.
- Commands expected to exceed 120 seconds must use a harness or CI.
- Full unittest discovery must not run inside AI sessions by default.
- Full discovery is a manual, nightly, or promotion gate.
- Full-discovery artifacts should be written outside the repo, normally under
  `../eureka-test-runs/<run-id>`, not `.aide.local/test-runs/`.
- If full discovery is required, create `external_full_discovery_handoff.json`
  and stop with `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`.
- AI should read `full_unittest_summary.json`, not full logs.
- Request targeted traceback excerpts only when needed.
