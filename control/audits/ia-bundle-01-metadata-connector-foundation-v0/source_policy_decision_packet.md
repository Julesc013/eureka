# Source Policy Decision Packet

Decision: `fixture_only_foundation`.

Internet Archive is classified as a preservation/source-metadata provider, not
canonical truth. IA-BUNDLE-01 does not approve live source access. Source policy
approval, User-Agent/contact, endpoint allowlist, rate limit, timeout/retry,
cache TTL, and kill switch decisions remain pending before IA-BUNDLE-02 can
request a bounded metadata-only live probe.

Current approvals:

- fixture normalization: approved
- fixture source-cache preview: approved
- fixture evidence-candidate preview: approved

Current denials:

- live IA calls
- external URL calls
- downloads
- file fetches
- scraping/crawling
- public query fanout
- source cache runtime writes
- evidence ledger runtime writes
- public/master index mutation
