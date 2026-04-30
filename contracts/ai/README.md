# AI Contracts

AI Provider Contract v0 defines optional future model-provider manifests,
typed task requests, and typed output envelopes. These contracts are
governance and validation only.

They do not implement AI provider runtime, model calls, API keys, credential
storage, prompt logging, telemetry, embeddings, vector search, LLM reranking,
AI extraction, public-search AI behavior, or master-index acceptance.

Current contracts:

- `ai_provider_manifest.v0.json`
- `ai_task_request.v0.json`
- `typed_ai_output.v0.json`

Every provider is disabled by default. Every AI output is a suggestion or
candidate that requires review and must not be used as canonical truth, rights
clearance, malware safety, source-trust authority, or automatic acceptance.
