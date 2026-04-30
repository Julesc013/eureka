# Live Probe Gateway

The live probe gateway is the future boundary between a hosted Eureka backend
and external metadata sources. It does not exist as runtime behavior yet.

The intended path is:

```text
static publication plane
  -> live backend handoff
  -> live probe gateway
  -> source-specific metadata adapters
```

The gateway is separate from Source Registry v0. The source registry describes
known source families, fixture posture, capabilities, limitations, and
placeholder honesty. The live probe gateway would decide whether a future
backend may contact a source at all, under which caps, and how the result is
cached and evidenced.

The gateway is also separate from recorded fixtures. Recorded fixtures are
committed repo inputs. Live probes would be fresh external observations and must
not silently replace fixture-backed truth.

Public Search API Contract v0 is also separate from this gateway. Its first
mode is `local_index_only`, so future public search must use a controlled local
index rather than live source fanout. Live probe modes remain disabled and are
not accepted by the v0 search request schema.
Public Search Result Card Contract v0 keeps `future_live_probe` as a source
posture label only. It does not enable live probes, external source calls, URL
fetching, or live source fanout.

## Anti-Crawl Boundary

The gateway is designed to prevent uncontrolled crawling:

- no arbitrary URL fetching
- no bulk crawl mode
- no downloads
- maximum source count per request
- maximum result count per source
- per-source timeout
- retry and circuit-breaker expectations
- per-source disable switch
- operator signoff before any source is enabled

## Evidence Boundary

Future probe output must produce evidence records with source id, probe mode,
limits, cache status, observation time, and a bounded response summary. Probe
results are not product truth unless they remain traceable and invalidatable.

## Manual Baselines

Manual external baselines are separate. Google web search remains
human-operated manual baseline evidence only; Eureka must not scrape Google or
automate Google searches through this gateway.

## Internet Archive

Internet Archive live probing comes after this contract. A future first probe
should be metadata-only, disabled by default, bounded by caps, cache-first, and
evidence-linked. This architecture document does not implement that probe.

Compatibility Surface Strategy v0 keeps live probes out of all current static,
lite, text, files, demo, snapshot, relay, and native-client plans unless a
future backend explicitly enables them through the gateway policy and operator
signoff.
