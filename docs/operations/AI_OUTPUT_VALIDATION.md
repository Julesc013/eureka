# AI Output Validation

Typed AI Output Validator v0 validates recorded AI output candidates without
calling a model.

Use:

```bash
python scripts/validate_ai_output.py
python scripts/validate_ai_output.py --json
python scripts/validate_ai_output.py --all-examples
python scripts/validate_ai_output.py --all-examples --json
python scripts/validate_ai_output.py --output examples/ai_providers/disabled_stub_provider_v0/examples/alias_candidate.valid.json
python scripts/validate_ai_output.py --bundle-root examples/ai_providers/disabled_stub_provider_v0
```

The command is offline, stdlib-only, and validation-only. It does not implement
model calls, runtime provider loading, prompt logging, telemetry, evidence
import, contribution import, pack import, local-index mutation, public-search
AI, upload, submission, or master-index mutation.

## What It Checks

The validator checks that typed outputs:

- use `typed_ai_output.v0`
- reference a known disabled-by-default provider manifest when supplied
- use allowed task and output types
- remain `suggestion`, `candidate`, `rejected`, `superseded`, or
  `accepted_for_review`
- set `required_review: true`
- prohibit `canonical_truth`, `rights_clearance`, `malware_safety`, and
  `automatic_acceptance`
- keep `generated_text` at or below 2000 characters
- include non-empty limitations
- keep structured claims as review-required candidates
- avoid API keys, secrets, credentials, private keys, and private absolute
  paths in public-safe output

Validation success does not prove truth, source trust, rights clearance,
malware safety, compatibility, identity, ranking quality, or master-index
acceptance.

## Example Outputs

The current valid examples are registered in
`control/inventory/ai_providers/typed_output_examples.json`:

- `alias_candidate.valid.json`
- `compatibility_claim_candidate.valid.json`
- `explanation_draft.valid.json`
- `metadata_claim_candidate.valid.json`

All are synthetic, hand-authored, and tied to
`example.disabled_stub_provider_v0`. Invalid output behavior is covered by
tempfile-based tests instead of committed invalid fixtures.

## Workflow Boundary

Future AI-assisted evidence drafting should run typed output validation first,
then preserve provider provenance, limitations, source refs, and evidence refs.
Validated AI output still does not enter evidence packs, contribution packs, or
the master index automatically. It remains a review-required candidate until a
future contribution or review workflow explicitly handles it.
