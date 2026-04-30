# Disabled Stub AI Provider v0

This is a synthetic, non-operational example for AI Provider Contract v0. It
exists only to validate manifest shape, typed output examples, checksums, and
safety policy.

The provider is disabled by default. It performs no model calls, opens no
network connection, reads no local user files, stores no credentials, logs no
prompts, emits no telemetry, and has no runtime integration.

The example outputs under `examples/` are hand-authored fixture outputs. They
are suggestions that require review, not evidence truth, rights clearance,
malware safety, identity authority, or master-index acceptance.

Typed AI Output Validator v0 validates the four current examples:

- `alias_candidate.valid.json`
- `compatibility_claim_candidate.valid.json`
- `explanation_draft.valid.json`
- `metadata_claim_candidate.valid.json`

Use `python scripts/validate_ai_output.py --bundle-root
examples/ai_providers/disabled_stub_provider_v0` to validate the bundle. The
command does not call a model, load this provider, import evidence, draft a
contribution, mutate search/index state, or submit to a master index.
