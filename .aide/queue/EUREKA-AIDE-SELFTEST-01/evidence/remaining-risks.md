# Remaining Risks

- Token measurement still uses `chars / 4`, not an exact tokenizer or provider
  billing integration.
- This repair proves the portable AIDE Lite selftest lane in Eureka, not
  arbitrary Eureka product implementation quality.
- Eureka-specific AIDE golden tasks remain future work and are the recommended
  next task.
- The target-local repair may need upstream synchronization into the AIDE source
  pack after review; this task does not mutate the AIDE repo.
- `verify` may remain WARN with 0 errors because the latest packet references
  future handoff evidence or optional imported reports that are not generated in
  this target repo.
- Broad unittest discovery includes source-pack export/import fixture tests that
  still assume full source-pack fixtures; those are outside this bounded
  selftest fallback repair.
