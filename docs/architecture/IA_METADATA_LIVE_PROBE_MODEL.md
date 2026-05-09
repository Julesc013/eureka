# IA Metadata Live Probe Model

IA-BUNDLE-02 introduces a live-probe envelope around the fixture-only
IA-BUNDLE-01 normalizer.

```text
policy bundle
  -> exact identifier approval
  -> one metadata endpoint request, if approved
  -> live probe result
  -> IA-BUNDLE-01 normalization
  -> source cache candidate preview
  -> evidence candidate preview
  -> review queue seed preview
```

The committed state stops at the policy gate. This is intentional: the runtime
exists, but the current policy files keep the live call disabled.

## Gate Model

The runtime requires all gates before network use:

- source live access approved
- metadata probe approved
- downloads, item fetches, scraping, and fanout still forbidden
- metadata endpoint is the only allowed endpoint
- User-Agent/contact posture approved
- timeout, request budget, retry, and cache/no-cache decisions approved
- kill switch allows the one run
- exact identifier is allowlisted

Any missing gate returns a blocked result with `request_count: 0`.

## Truth Model

A live IA metadata response is not truth. It cannot prove identity, rights,
malware safety, installability, completeness, public-index membership, or
master-index acceptance.

The live-probe model prepares IA-BUNDLE-03 by producing reviewable previews
only after a future operator-approved live run.
