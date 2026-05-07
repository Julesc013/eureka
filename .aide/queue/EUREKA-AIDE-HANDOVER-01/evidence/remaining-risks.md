# Remaining Risks

- Q26 proves readiness for the next bounded Eureka task, not broad autonomous
  implementation quality.
- The token estimate uses chars/4 and is not an exact tokenizer or provider
  billing measurement.
- Provider routing, Gateway execution, live model calls, and enforcement remain
  out of scope and disabled.
- `test` and `selftest` still fail in the imported temp-fixture path after the
  Q25 portable refresh; this is the selected next bounded task.
- Eureka-specific golden tasks are still pending until after the selected
  selftest repair task.
- The repaired Q25 importer is safe-scoped, but Eureka still needs review of
  any future full-mode import before broad roots are copied.
- Broader product implementation should wait until the Q26 handover review
  accepts this limitation or the next task fixes it.
