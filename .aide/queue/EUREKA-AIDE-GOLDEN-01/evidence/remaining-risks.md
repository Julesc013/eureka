# Remaining Risks

- Golden tasks are deterministic metadata checks, not arbitrary coding-quality
  proof.
- Exact tokenization, cached-token discounts, hidden reasoning tokens, and
  provider billing are still not measured.
- Broad unittest discovery may still expose unrelated export/import fixture
  assumptions outside this target golden-task lane.
- The Eureka-specific task suite may need upstream AIDE Lite hooks or policy
  formalization later.
- The next task must stay bounded and low-risk; product implementation remains
  deferred until one real AIDE-driven maintenance task proves value.
