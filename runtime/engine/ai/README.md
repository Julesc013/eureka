# Runtime Engine AI Validation

This package contains validation-only helpers for AI Provider Contract v0 and
Typed AI Output Validator v0.

It does not implement AI provider runtime behavior, model calls, local model
execution, remote API calls, embeddings, vector search, prompt logging,
telemetry, public-search AI, evidence import, contribution import, local-index
mutation, or master-index acceptance.

The first module, `typed_output_validator.py`, validates recorded typed AI
output candidates as suggestions that require review. It is intentionally
offline and stdlib-only so future tooling can call it before any AI-assisted
evidence or contribution workflow is considered.
