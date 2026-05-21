# F0 Extraction Member Discovery

F0 is the fixture-only and manifest-only foundation for extraction/member discovery. It lets Eureka describe and enumerate tiny committed fixtures so later work can reason about members inside archives, packages, support media, scans, and source bundles without opening a production extraction surface.

F0 member discovery is not truth. Member paths are observations that require review before they can influence evidence, candidates, reviewed records, or indexes. The foundation makes no downloads, performs no filesystem extraction, performs no execution, and does not create fake evidence or verified records.

The initial pipeline is:

1. DOMAIN, SCOUT, SYN, IA, or Hunt hint suggests a container may matter.
2. F0 policy checks the request.
3. A safe committed fixture or descriptor is enumerated as a member manifest.
4. Member observations can seed future WorkUnits, still review-gated.

The incorrect pipeline remains forbidden: arbitrary file to extract everything to accepted evidence to reviewed truth. F0 has no arbitrary local file extraction, no source fetch, no install/emulation, no model calls, and no master/public index mutation.

Future F0 work can add carefully reviewed container-specific policies, but those tasks must preserve review gates and keep unsafe actions blocked by default.
