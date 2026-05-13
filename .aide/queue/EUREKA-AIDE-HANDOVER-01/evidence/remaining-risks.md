# Remaining Risks

- Q26 proves readiness for compact AIDE Lite handoff, not broad autonomous
  implementation quality.
- The token estimate uses chars/4 and is not an exact tokenizer or provider
  billing measurement.
- Provider routing, Gateway execution, live model calls, and enforcement remain
  out of scope and disabled.
- Safe import from the Q25 AIDE source pack now reports target conflicts because
  Eureka's imported AIDE state has evolved; future pack sync needs a reviewed
  target task.
- Target `pack-status` is not applicable because Eureka does not carry the
  source export pack under `.aide/export/aide-lite-pack-v0`.
- LOCAL-04 has a product validation preflight blocker:
  `scripts/validate_local_runtime_composition.py` fails because the current
  leakage scan exceeds the recorded LOCAL-03 baseline.
- The broader runtime architecture leakage and legacy remediation validators
  also fail against current `dev`; those product-governance findings are outside
  Q26's allowed edit scope.
- The git task-state guard warns that Q26 revalidation ran on `dev` rather than
  a same-named task branch.
- Route classification remains conservative (`frontier` / human review fallback)
  because the current packet is not mapped to a known AIDE task class.
