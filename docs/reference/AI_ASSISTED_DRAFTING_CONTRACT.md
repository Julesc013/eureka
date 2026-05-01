# AI-Assisted Drafting Contract

AI-Assisted Drafting Contract v0 is a planning contract for AI-assisted
evidence drafting. It defines how future AI output may become evidence
candidates or contribution candidates. It does not call models, load
providers, store credentials, enable telemetry, process private data, import
evidence, submit contributions, mutate search, mutate local indexes, or mutate
the master index.

Boundary summary: there is no runtime, no model calls, no automatic acceptance,
and AI output is not truth. Typed output validation and required review are
mandatory before any future evidence candidates or contribution candidates can
enter a review workflow.

## Workflow

The only allowed future workflow is:

1. validate source/evidence/result/staging context
2. create an explicit AI task request
3. select a disabled-by-default provider under policy
4. receive typed AI output
5. run `scripts/validate_ai_output.py`
6. map validated output to a candidate
7. require human or governed review

Validation success means the output is structurally acceptable as a candidate.
It does not mean the claim is true, rights-cleared, safe to execute, trusted,
accepted by public search, accepted by a contribution workflow, or accepted by
the master index.

## Allowed Task Mappings

| Drafting task | Typed output | Future candidate |
| --- | --- | --- |
| `draft_alias_candidate` | `alias_candidate` | contribution `alias_suggestion` |
| `draft_metadata_claim_candidate` | `metadata_claim_candidate` | evidence `metadata_claim` or contribution `evidence_record_candidate` |
| `draft_compatibility_claim_candidate` | `compatibility_claim_candidate` | evidence `compatibility_claim` or contribution `compatibility_suggestion` |
| `draft_review_description_claim_candidate` | `review_claim_candidate` | evidence `review_description_observation` |
| `draft_member_path_claim_candidate` | `member_path_candidate` | evidence `member_path_claim` |
| `draft_source_match_candidate` | `source_match_candidate` | contribution `source_record_candidate` or evidence `source_observation` |
| `draft_identity_match_candidate_for_review` | `identity_match_candidate` | contribution `duplicate_or_identity_candidate` |
| `draft_explanation_text` | `explanation_draft` | result explanation draft only |
| `draft_absence_explanation` | `absence_explanation_draft` | absence report candidate |
| `draft_contribution_item_candidate` | `contribution_draft_candidate` | `contribution_items.jsonl` candidate |
| `draft_evidence_pack_record_candidate` | candidate output type matching record | evidence record candidate |

Every mapping requires typed output validation, provenance/source references
where possible, privacy review, rights/risk review, and required review. No
mapping grants automatic acceptance.

## Input Context Classes

Public-safe input contexts:

- public search result card
- public source summary
- public evidence summary
- public snippet already allowed by evidence pack policy
- public static demo record
- synthetic fixture record
- public-safe pack record

Local/private input contexts:

- local staged pack manifest
- local private source pack
- local private evidence pack
- local cache metadata
- user notes
- local file metadata
- user-selected private snippets

Forbidden by default for remote AI:

- private local paths
- credentials or secret values
- raw private files
- raw local caches
- long copyrighted text
- executable payloads
- unredacted user search history
- unreviewed private source records

## Prohibited Outputs

AI output must not claim canonical truth, rights clearance, malware safety,
source-trust finality, automatic identity merge, public-search mutation,
local-index mutation, contribution acceptance, or master-index acceptance.

## Future Prerequisites

Before any runtime exists, Eureka needs explicit approval for provider loading,
task request generation, local/private input controls, remote-provider consent,
credential handling, prompt/output logging policy, candidate export, review UI
or review workflow, and no-mutation verification.
