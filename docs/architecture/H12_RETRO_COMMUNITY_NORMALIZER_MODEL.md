# H12 Retro Community Normalizer Model

H12-BUNDLE-02 is a fixture-only runtime for committed synthetic retro/community archive metadata. It proves parsing, normalization, candidate construction, replay summaries, and blocked-boundary behavior without approving access.

The runtime may produce normalized retro/community records, retro software identity candidates, platform/version/edition candidates, archive item/member candidates, compatibility/install-note candidates, community review/comment candidates, hash/checksum candidates, IA/Wayback corroboration candidates, gated-source boundary candidates, retro rights/safety candidates, source-cache previews, evidence previews, and fixture replay reports.

It must not perform live source calls, API/catalog/forum/gated fetches, downloads, extraction, execution, acquisition actions, uploads, hash submissions, scraping, crawling, browser automation, bypass, source sync, source-cache writes, evidence acceptance, public-index mutation, master-index mutation, or truth acceptance.

All outputs are candidates or previews. Metadata does not prove retro software identity, platform/version truth, file authenticity, checksum correctness, compatibility correctness, installability, playability, legal acquisition, rights clearance, malware safety, content safety, privacy safety, community reputation, verified authenticity, production readiness, or acquisition permission.

H12-BUNDLE-02 prepares H12-BUNDLE-03 by making fixture-equivalent outputs available for a future approval-gated metadata-only live-probe envelope.

Validation:

- `python scripts/validate_h12_retro_community_fixture_runtime.py`
- `python scripts/replay_h12_retro_community_fixtures.py --check`
- `python scripts/summarize_h12_retro_community_fixture_outputs.py --input examples/connectors/h12_retro_community --check`
