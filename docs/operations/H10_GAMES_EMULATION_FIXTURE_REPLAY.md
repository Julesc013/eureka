# H10 games/emulation fixture replay

H10-BUNDLE-02 is fixture-runtime work for games, emulation, software-list, preservation hash-set, ROM/disc/media identity, compatibility, relation, action-candidate, and rights/safety metadata.

It reads only committed synthetic fixtures and emits normalized records, candidates, source-cache previews, evidence previews, and fixture replay reports. It does not perform live source calls, network/API/model/provider calls, catalog queries, software-list or hash-set fetches, downloads, uploads, hash submissions, emulator/game/install execution, acquisition actions, scraping, crawling, browser automation, bypass behavior, restricted-source access, source-cache writes, evidence writes, review queue writes, public-index mutation, or master-index mutation.

Candidate outputs are review material only. Game/software identity, platform/release/edition, emulator compatibility, preservation hash-set, ROM/disc/media identity, game relation, emulator/action, and rights/safety candidates do not accept source truth, evidence truth, candidate truth, public truth, identity truth, relation truth, compatibility correctness, hash-set truth, action permission, legal acquisition, rights clearance, authenticity, playability, installability, malware safety, content safety, privacy safety, verified authenticity, or production readiness.

The fixture runtime prepares H10-BUNDLE-03 by proving offline parsing and boundary behavior before any future approval-gated metadata-only live probes.

Validation:

```powershell
python scripts/validate_h10_games_emulation_fixture_runtime.py
python scripts/normalize_h10_games_emulation_fixture.py --source-id mobygames --input examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json --check
python scripts/replay_h10_games_emulation_fixtures.py --check
python scripts/summarize_h10_games_emulation_fixture_outputs.py --input examples/connectors/h10_games_emulation --check
```
