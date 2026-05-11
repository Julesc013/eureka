# H10 Games Emulation Live Probe Restricted Source Policy

H10 games/emulation live probes are approval-gated metadata observation envelopes for game/software identity, platform/release/edition metadata, emulator compatibility observations, preservation hash-set metadata, ROM/disc/media identity candidates, game relation candidates, emulator/action blocked candidates, and rights/safety candidates.

They are not live access approval, source sync, catalog harvesting, software-list or hash-set fetching, downloads, uploads, hash submissions, emulator/game/install execution, acquisition actions, scraping, crawling, browser automation, bypass, restricted-source access, accepted evidence, accepted candidates, accepted game/release/platform/emulator/hash-set/ROM-disc/relation/action/rights/safety truth, public-index mutation, master-index mutation, verified authenticity, compatibility correctness, legal acquisition, rights clearance, safety proof, or production readiness.

Default operation is offline preflight. If an exact source-specific request lacks committed approval, the probe emits a blocked result before any network path can run. All examples in this bundle are dry-run or blocked fixture-equivalent outputs with `network_used: false`.

Validation:

```bash
python scripts/validate_h10_games_emulation_live_probe.py
python scripts/run_h10_games_emulation_live_probe.py --source-id mobygames --request-key example_game_metadata --check
python scripts/summarize_h10_games_emulation_live_probe_outputs.py --input examples/connectors/h10_games_emulation/live_probe_results --check
```
