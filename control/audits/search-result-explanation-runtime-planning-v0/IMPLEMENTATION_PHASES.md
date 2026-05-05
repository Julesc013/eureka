# Implementation Phases

Phase 0: keep runtime disabled and complete planning and validation.

Phase 1: local dry-run explanation assembler over synthetic examples only. No
public search response changes.

Phase 2: local shadow explanation generation from public search smoke result
envelopes. Results returned to callers remain unchanged; explanations are
written only to test reports.

Phase 3: local visible explanations in development only. No hosted deployment.

Phase 4: hosted staging explanations behind a disabled-by-default flag. Safety
and privacy tests are required.

Phase 5: public alpha explanations with fallback and kill switch. No model calls,
hidden scores, suppression, telemetry, live sources, or mutation.

