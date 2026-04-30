# AI Assistance Boundary

AI assistance is optional and future. Eureka's current core remains
deterministic, evidence-linked, and usable without model providers.

AI Provider Contract v0 defines the boundary before runtime integration:

- providers are disabled by default
- manifests are not executable plugins
- validation does not call models
- private data is disabled by default
- telemetry and prompt/output logging are disabled by default
- remote providers require explicit credentials and consent before future use
- outputs are typed suggestions or candidates
- outputs require review
- AI is not truth, rights clearance, malware safety, source trust, or automatic
  acceptance

## Local, Remote, Browser, Native, And Development Providers

Local model and local server provider types describe future local-only
integration classes. They do not grant arbitrary filesystem access or live
source access.

Remote API provider types describe future hosted model API classes. They remain
disabled until a separate runtime, consent, credential, and logging policy is
approved.

Browser and native model provider types are future surface integrations only.
They do not exist in current web/native surfaces.

Development-tool providers describe repo development contexts such as AIDE or
Codex. AIDE/Codex can help maintain the repo, but that does not make them
product runtime AI providers.

## Relationship To Evidence And Review

AI output can draft an alias candidate, compatibility candidate, explanation
draft, source match candidate, or contribution draft candidate. It cannot turn
a draft into evidence truth. Future workflows must keep provider provenance,
source/evidence links, limitations, and review status attached to every output.

The Master Index Review Queue remains the governance point for future public
acceptance. AI output can enter that path only as a candidate with explicit
review and provenance.

## Public Search Boundary

Public search remains local/prototype and `local_index_only`. AI Provider
Contract v0 does not add public-search AI, hosted search AI, model reranking,
query expansion, semantic/vector search, embeddings, generated snippets, or
result explanation runtime.

## Deferred Runtime Work

Future runtime work needs separate approval for provider loading, consent UI,
credential handling, prompt/output logging policy, cache invalidation,
private-data redaction, typed-output validation at runtime, contribution-pack
drafting, review queue export, and any public-search display.
