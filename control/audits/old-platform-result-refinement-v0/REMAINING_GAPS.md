# Remaining Gaps

`latest_firefox_before_xp_drop`

- Needs exact latest-compatible release/version evidence.
- Needs direct release asset or installer locator evidence.
- Follow-up: More Source Coverage Expansion v1 adds bounded Firefox XP
  52.9.0 ESR candidate evidence and the current hard eval now satisfies its
  strict fixture-backed checks. This remains fixture-scoped evidence, not a
  global latest-version oracle.

`old_blue_ftp_client_xp`

- Needs concrete product identity or direct installer evidence.
- Vague identity remains intentionally uncertain.
- Follow-up: More Source Coverage Expansion v1 adds direct blue FTP-client XP
  candidate member/artifact evidence and the current hard eval now satisfies
  the fixture-backed checks without claiming universal real-world identity.

`win98_registry_repair`

- Needs a primary result lane/shape that is direct or installable rather than
  preservation/context.
- Follow-up: More Source Coverage Expansion v1 strengthens the Windows 98
  registry repair bundle/artifact evidence and the current hard eval now
  satisfies the strict source-backed checks.

`windows_7_apps`

- Needs result-lane/user-cost refinement so direct app representations are not
  presented as parent-bundle context.
- Follow-up: More Source Coverage Expansion v1 adds additional Windows 7
  utility/app fixture members and the current hard eval now satisfies the
  strict source-backed checks without claiming broad app-catalog coverage.

`article_inside_magazine_scan`

- Needs bounded scan/OCR/article/page evidence before it can leave
  `capability_gap`.
- Still open after More Source Coverage Expansion v1; no scan/page/OCR/article
  evidence was added.

Deferred:

- live crawling
- Google scraping
- Internet Archive scraping or live API calls
- arbitrary local filesystem ingestion
- fuzzy/vector/LLM retrieval
- production ranking
- Rust behavior ports
- native app work
- external baseline claims without manual evidence
