# Implementation Phases

Phase 0: keep disabled; complete planning and validation.

Phase 1: local dry-run ranker over synthetic examples and existing public index fixtures only; no public search response changes.

Phase 2: local shadow-ranking mode; current order returned and proposed order logged only to test report, not telemetry.

Phase 3: local visible ranking with explanations in development only; no hosted deployment.

Phase 4: hosted staging ranking behind disabled-by-default flag with full safety/eval gate.

Phase 5: public alpha ranking with current-order fallback and user-visible explanations; no source/evidence/candidate/master mutation.
