# H10 ROM Disc Media Identity Policy

ROM, disc, and media identity fields such as hashes, serial candidates, product codes, regions, languages, and related releases remain candidates only.

        ## Scope

        This document belongs to H10-BUNDLE-01 and is policy-pack-only. It prepares H10-BUNDLE-02 fixture runtime work and H10-BUNDLE-03 approved metadata-only probe design without enabling those behaviors now.

        ## Boundary

        H10-BUNDLE-01 does not enable live access, API/catalog queries, software-list or hash-set fetches, downloads, uploads, hash submissions, emulator/game/install execution, acquisition actions, scraping, crawling, bypass, restricted-source access, source sync, public/master index mutation, or source/evidence/candidate/game/release/platform/emulator/hashset/ROM-disc/relation/action/rights/safety truth acceptance.

        ## Validation

        Run `python scripts/validate_h10_games_emulation_policy_packs.py` and `python scripts/summarize_h10_games_emulation_sources.py --check`.
