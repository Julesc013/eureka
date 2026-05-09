# IA-BUNDLE-01 Metadata Connector Foundation

Status: `pass_with_warnings`.

IA-BUNDLE-01 adds the fixture-only Internet Archive metadata connector
foundation. It creates source policy, endpoint allow/deny posture,
User-Agent/contact/rate/cache/kill-switch policy records, committed fixtures,
fixture normalization, source-cache preview mapping, evidence-candidate preview
mapping, tests, and validation.

No Internet Archive live call, external call, live probe, source sync, download,
file fetch, scraping, public query fanout, source-cache runtime mutation,
evidence-ledger runtime mutation, public-index mutation, master-index mutation,
evidence acceptance, candidate acceptance, or public truth creation is enabled.

The only remaining warnings are AIDE review-packet references to optional
controller, gateway, and provider status artifacts that are not present in this
repo snapshot. AIDE verify reports zero errors.

## Generated Evidence

- `generated/sample_normalized_ia_metadata.json`
- `generated/sample_source_cache_candidate.json`
- `generated/sample_evidence_candidate_preview.json`
