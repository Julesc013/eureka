# AI-Assisted Evidence Drafting

AI-Assisted Evidence Drafting Plan v0 defines a future workflow for using
optional AI providers as drafting assistants. It does not implement AI runtime,
provider loading, prompt logging, telemetry, model calls, evidence import,
contribution import, public-search mutation, local-index mutation, or
master-index mutation.

Boundary summary: there is no runtime, no model calls, no automatic acceptance,
and AI output is not truth. Typed output validation and required review are
mandatory before any future evidence candidates or contribution candidates can
enter a review workflow.

The safe shape is:

1. Start from validated source, evidence, result-card, staged-manifest, or pack
   context.
2. Create an explicit future AI task request with provider, privacy, and input
   policy.
3. Use a provider that remains disabled by default until a later approved
   runtime exists.
4. Validate the typed AI output with `scripts/validate_ai_output.py`.
5. Convert only validated output into an evidence or contribution candidate.
6. Send the candidate through human or governed review.

AI is an assistant, not authority. A model may draft an alias candidate,
metadata claim candidate, compatibility claim candidate, source-match
candidate, identity-match candidate for review, explanation draft, absence
explanation draft, evidence-pack record candidate, or contribution item
candidate. It may not decide canonical truth, rights clearance, malware safety,
source trust, identity merge, public-search ranking, local-index contents, or
master-index acceptance.

Public-safe context includes public result cards, source summaries, evidence
summaries, evidence-policy-compliant snippets, synthetic fixtures, static demo
records, and public-safe pack records. Local/private context includes staged
pack manifests, private source or evidence packs, local cache metadata, user
notes, local file metadata, and user-selected private snippets. Local/private
context must stay local/private by default and must not be sent to remote
providers unless a later explicit policy, consent, credential, and logging
review authorizes it.

Remote providers remain disabled by default. Local providers also remain
disabled by default until a separate runtime milestone exists. Development
tools such as Codex may help edit repository planning documents, but AIDE and
development tooling remain repo-operating metadata, not product runtime AI
providers.

Evidence packs and contribution packs remain candidate containers. Typed AI
output can later map to evidence or contribution candidates only after typed
validation, provenance/source references where possible, privacy review, and
human or governed review. Master Index Review Queue Contract v0 remains the
separate acceptance boundary; no AI output can auto-accept a master-index
record.

Public search remains local_index_only and local/prototype. AI-assisted
drafting must not change search ranking, result cards, source registry records,
local indexes, static site data, hosted search state, or master-index state by
default.

Future implementation prerequisites include an approved AI task request
runtime, provider selection UI or operator policy, consent and private-data
handling policy, credential storage policy if remote providers are ever used,
prompt/output logging policy, local/private redaction gates, candidate export
format, review workflow, and explicit no-mutation verification.
