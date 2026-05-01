# AI Provider Inventory

This inventory records AI Provider Contract v0 policy and non-operational
example provider metadata. It is contract-only governance material.

No AI provider runtime, model call, API key, credential store, prompt logging
runtime, telemetry, embeddings, vector search, LLM reranking, public-search AI,
or automatic evidence acceptance is implemented.

Typed AI Output Validator v0 adds `typed_output_examples.json` and
`scripts/validate_ai_output.py` for offline validation of recorded typed output
candidates. It does not call models, load providers, import evidence, create
contribution records, mutate local indexes, upload, or mutate a master index.

AI-Assisted Evidence Drafting Plan v0 adds
`ai_assisted_drafting_policy.json` for future candidate drafting policy. It is
planning-only and keeps AI disabled by default, remote providers disabled by
default, private data disabled by default, typed output validation required,
and review required. It adds no model calls, runtime provider loading,
telemetry, evidence acceptance, contribution acceptance, public-search
mutation, local-index mutation, or master-index mutation.
