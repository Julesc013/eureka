# Contract Summary

AI Provider Contract v0 defines provider manifests, future task requests, and
typed output envelopes for optional AI assistance.

Implemented:

- `contracts/ai/ai_provider_manifest.v0.json`
- `contracts/ai/typed_ai_output.v0.json`
- `contracts/ai/ai_task_request.v0.json`
- `control/inventory/ai_providers/`
- `examples/ai_providers/disabled_stub_provider_v0/`
- `scripts/validate_ai_provider_contract.py`

Not implemented: model calls, runtime provider loading, API keys, credential
storage, telemetry, prompt logging runtime, embeddings, vector search, LLM
reranking, public-search AI, AI evidence acceptance, local index mutation, or
master-index mutation.
