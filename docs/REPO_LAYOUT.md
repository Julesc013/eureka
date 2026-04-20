# Repo Layout

The intended bootstrap tree is:

```text
eureka/
  .aide/
    components/
    commands/
    policies/
    evals/
    compat/
  control/
    governance/
    inventory/
    matrices/
    research/
    packaging/
  contracts/
    archive/
      schemas/
      protocols/
      versions/
      fixtures/
      trust/
    gateway/
      public_api/
    ui/
      view_models/
      ui_contracts/
  docs/
  runtime/
    engine/
      core/
      ingest/
      extract/
      identify/
      normalize/
      resolve/
      index/
      actions/
      snapshots/
      sdk/
      tests/
    gateway/
      public_api/
      broker/
      relay/
      workers/
      scheduler/
      auth/
      publishing/
      tests/
    connectors/
      structured_web/
      repository_harvest/
      preservation/
      web_archives/
      package_ecosystems/
      tests/
  surfaces/
    web/
      server/
      workbench/
      pages/
      static/
      tests/
    native/
      shared/
      cli/
      tui/
      shell/
        windows/
        macos/
        linux/
        android/
        ios/
      integrations/
      local_cache/
      local_actions/
      tests/
  tests/
    integration/
    end_to_end/
  evals/
    system/
    replay/
  scripts/
  third_party/
```

## Ownership Intent

- `control/`: governance and planning assets; not runtime behavior
- `contracts/`: governed assets that define shared meaning and public boundaries
- `docs/`: founding documents, bootstrap status, and decision records
- `runtime/`: implementation areas for the engine, gateway, and connectors
- `surfaces/`: user-facing web and native applications
- `tests/`: root integration and end-to-end verification that crosses component boundaries
- `evals/`: root system and replay evaluations used to measure behavior over time
- `scripts/`: repo support scripts when lightweight automation becomes necessary
- `third_party/`: pinned or vendored external materials, kept separate from product semantics

## Test Boundary

Component-local tests live inside the component they validate, such as `runtime/engine/tests`, `runtime/gateway/tests`, `runtime/connectors/tests`, `surfaces/web/tests`, or `surfaces/native/tests`. These should stay close to the implementation boundary they exercise.

Root `tests/` is reserved for cross-component integration and end-to-end coverage. Root `evals/` is reserved for system-level and replay-style evaluation, not unit-style component checks.
