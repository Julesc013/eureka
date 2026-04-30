# Runtime Boundaries

This milestone adds validation code only.

It does not implement:

- AI provider runtime loading
- local model execution
- remote model API calls
- browser AI
- embeddings or vector search
- LLM reranking
- prompt logging or telemetry
- evidence import
- contribution import
- local index mutation
- public-search AI
- upload, submission, moderation, accounts, or master-index mutation

The validation module under `runtime/engine/ai/` is not a provider runtime. It
is pure offline validation logic.
