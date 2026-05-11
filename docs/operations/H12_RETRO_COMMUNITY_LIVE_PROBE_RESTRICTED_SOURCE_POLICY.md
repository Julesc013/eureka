# H12 Retro/Community Live Probe Restricted Source Policy

H12-BUNDLE-03 defines an approval-gated metadata-only live-probe framework for retro and community archive sources.

Current status: fail closed. The default behavior is offline validation, dry preflight, and blocked output when committed source-specific approval is missing. This document does not grant live access.

Allowed current outputs are live-probe result envelopes, normalized record previews, retro software identity candidates, platform/version/edition candidates, archive item/member candidates, compatibility/install-note candidates, community review/comment candidates, hash/checksum candidates, IA/Wayback corroboration candidates, gated-source boundary candidates, retro rights/safety candidates, source-cache previews, evidence previews, review seed previews, connector health summaries, and blocked/preflight summaries.

Forbidden current behavior includes broad retro/archive/forum search, source sync, public query fanout, unapproved API/catalog/forum/web-archive queries, gated-source access, account access, downloads, extraction, execution, acquisition actions, uploads, hash submissions, scraping, crawling, browser automation, restricted-source access, bypass, public-index mutation, master-index mutation, and any source/evidence/candidate/public truth acceptance.

Community-lane trust remains candidate-only. Metadata presence does not prove retro software identity, platform/version truth, file authenticity, checksum correctness, rights clearance, legal acquisition, compatibility, installability, playability, malware safety, content safety, privacy safety, community reputation, verified authenticity, or production coverage.

Future live probing requires exact committed approval for one source and request key, endpoint/metadata-class allowlist, no-auth posture, User-Agent/contact posture where applicable, rate limit, timeout, retry budget, cache/no-cache decision, kill switch, output path allowlist, review policy, truth policy, no-download/no-execute policy, and restricted-source policy.

Validation:

```text
python scripts/validate_h12_retro_community_live_probe.py
python scripts/run_h12_retro_community_live_probe.py --source-id winworld_metadata --request-key example_catalog_item_metadata --check
python scripts/summarize_h12_retro_community_live_probe_outputs.py --input examples/connectors/h12_retro_community/live_probe_results --check
```
