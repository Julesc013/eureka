# H10 Game Relation Policy

Relations such as release_of_game, port_of_game, compatible_with_emulator, manual_for_game, storefront_listing_for_game, and hash_matches_media_candidate require review and do not become relation truth.

        ## Scope

        This document belongs to H10-BUNDLE-01 and is policy-pack-only. It prepares H10-BUNDLE-02 fixture runtime work and H10-BUNDLE-03 approved metadata-only probe design without enabling those behaviors now.

        ## Boundary

        H10-BUNDLE-01 does not enable live access, API/catalog queries, software-list or hash-set fetches, downloads, uploads, hash submissions, emulator/game/install execution, acquisition actions, scraping, crawling, bypass, restricted-source access, source sync, public/master index mutation, or source/evidence/candidate/game/release/platform/emulator/hashset/ROM-disc/relation/action/rights/safety truth acceptance.

        ## Validation

        Run `python scripts/validate_h10_games_emulation_policy_packs.py` and `python scripts/summarize_h10_games_emulation_sources.py --check`.
