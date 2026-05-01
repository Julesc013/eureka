# AI Provider Contract v0

AI Provider Contract v0 defines how future optional model providers can be
described before any AI runtime exists. A provider manifest records provider
type, supported tasks, output types, network and credential requirements,
privacy posture, logging posture, cache posture, evidence-linking rules, and
human-review requirements.

This contract is validation/example-only. It does not implement model calls,
OpenAI/Anthropic/Ollama/LM Studio calls, local model execution, provider
loading, API keys, credential storage, prompt logging runtime, telemetry,
embeddings, vector search, LLM reranking, AI extraction runtime, AI in public
search, or master-index acceptance.
Local Quarantine/Staging Model v0 may later stage typed AI output candidates
only as local_private, review-required metadata linked to validation reports.
It does not implement AI provider runtime, model calls, search mutation, or
master-index mutation.

## Provider Types

Provider manifests can describe these future provider classes:

- `local_model`: direct local runtime such as a future llama.cpp-style lane
- `local_server`: local loopback provider class such as future Ollama or LM
  Studio style integrations
- `remote_api`: hosted model API provider class requiring explicit credentials
  and approval before any future runtime exists
- `browser_model`: browser-provided local or on-device model class
- `native_model`: native-client model integration class
- `development_tool`: repository development tooling such as AIDE/Codex context,
  not product runtime behavior
- `disabled_stub`: non-operational fixture provider for contract tests

Every provider is disabled by default. AIDE/Codex may help develop the repo,
but it is not a product runtime AI provider unless a future explicit provider
runtime is separately approved and implemented.

## Manifest

`contracts/ai/ai_provider_manifest.v0.json` defines `AI_PROVIDER.json`.

Required manifest posture:

- `default_enabled: false`
- private data disabled by default
- telemetry and prompt/output logging disabled by default
- credentials never stored in the manifest
- remote providers require explicit credentials and operator/user approval
- no local filesystem access or live source access is granted by a manifest
- outputs are suggestions/candidates only
- all outputs require review
- master-index acceptance requires a separate review queue path

## Allowed Tasks

Allowed task types are bounded suggestion tasks:

- `query_interpretation_suggestion`
- `alias_suggestion`
- `metadata_extraction_suggestion`
- `compatibility_claim_candidate`
- `review_description_claim_extraction`
- `member_path_candidate_extraction`
- `source_matching_suggestion`
- `duplicate_identity_candidate`
- `explanation_draft`
- `OCR_cleanup_suggestion`
- `absence_explanation_draft`
- `contribution_pack_draft_assist`

These are candidate-producing tasks. They do not change search ranking, mutate
records, accept evidence, or write the master index.

## Forbidden Tasks

Forbidden task/output roles include:

- canonical truth decisions
- source-trust final decisions
- rights-clearance decisions
- malware-safety decisions
- automatic identity merge
- automatic master-index acceptance
- silent private data processing
- unbounded web browsing
- arbitrary URL fetch
- credential extraction
- installer/download execution
- telemetry collection

AI cannot determine rights clearance or malware safety for Eureka. AI output is
not source truth, identity truth, or source trust.

## Privacy, Credentials, And Logging

Local providers can be powerful, but private data remains local by default.
Remote providers require explicit credentials, explicit consent, and separate
runtime policy before any call can exist.

No provider manifest may contain API keys, source credentials, tokens, cookies,
private keys, account state, or endpoint secrets. No telemetry is implemented.
Future prompt or output logging must be off by default and governed by the
Telemetry and Logging Policy before it exists.

## Relationship To Packs

Source packs, evidence packs, index packs, and contribution packs remain the
governed containers for source metadata, claims, coverage summaries, and review
candidates. AI outputs may later help draft candidates for those packs, but
they must first be typed, validated, evidence-linked where possible, and
reviewed.

AI outputs do not bypass pack validation, pack import planning, contribution
review, or the Master Index Review Queue Contract. An AI suggestion cannot
become `accepted_public` without future review with provenance and limitations.

Typed output validation is now provided by
`runtime/engine/ai/typed_output_validator.py` and
`scripts/validate_ai_output.py`. This validator checks typed AI output examples
offline before any future evidence or contribution workflow may consider them.
It does not implement model calls, provider loading, prompt logging, telemetry,
evidence import, contribution import, local-index mutation, public-search AI, or
master-index mutation.

Pack Import Report Format v0 may record typed AI output validation results as
`ai_output_bundle` entries in future validate-only reports. Such reports do not
accept AI output as evidence, contribution material, truth, rights clearance,
malware safety, or master-index input.

## Public Search

Public search remains `local_index_only` and does not use AI providers. This
contract does not add AI result explanations, AI reranking, AI query expansion,
AI evidence extraction, embeddings, vector search, or remote model calls to
public search.

## Validation

Validate the contract and disabled stub provider:

```bash
python scripts/validate_ai_provider_contract.py
python scripts/validate_ai_provider_contract.py --json
python scripts/validate_ai_provider_contract.py --strict
```

Validate typed output examples directly:

```bash
python scripts/validate_ai_output.py
python scripts/validate_ai_output.py --json
python scripts/validate_ai_output.py --all-examples
python scripts/validate_ai_output.py --all-examples --json
```

The validator checks schema JSON, provider inventory, example manifest,
typed-output examples, checksums, disabled-by-default posture, credential and
privacy rules, logging/telemetry defaults, forbidden tasks and uses, no API
keys or secrets, and no AI provider runtime directories. The validation-only
module under `runtime/engine/ai/` is allowed solely for typed output validation;
it is not provider runtime behavior.

## Not Implemented

AI Provider Contract v0 does not implement model calls, runtime provider
loading, API keys, credential storage, prompt logging runtime, telemetry,
browser AI, local model execution, remote model APIs, embeddings, vector
search, LLM reranking, AI extraction runtime, AI-generated evidence
acceptance, local index mutation, public-search AI, uploads, accounts, relay
runtime, native client runtime, master-index mutation, rights clearance,
malware safety, or production AI support.

## AI-Assisted Drafting Plan

AI-Assisted Evidence Drafting Plan v0 is documented in
`docs/architecture/AI_ASSISTED_EVIDENCE_DRAFTING.md` and
`docs/reference/AI_ASSISTED_DRAFTING_CONTRACT.md`. It keeps providers disabled
by default and defines only future candidate drafting. It adds no runtime AI,
no model calls, no API keys, no telemetry, no provider loading, and no public
search, local index, runtime, contribution, evidence, or master-index mutation.

Future drafting must start from an explicit task request, run typed output
validation, and preserve required review. Output remains a candidate, not
truth, rights clearance, malware safety, source trust, automatic acceptance, or
master-index acceptance.
