# Old Client Degradation Policy

Eureka does not try to make one modern web app support every old client.
Compatibility comes from multiple read-only projections of the same resolver
truth.

Preferred fallback order:

1. current static public site for normal browsers
2. `/lite/` for old GUI browsers and low-capability HTML clients
3. `/text/` for text browsers, terminals, screen readers, and simple automation
4. `/files/` and `/data/` for file-tree clients and mirrors
5. future signed snapshots for offline or TLS-limited systems
6. future local relay for systems that cannot consume modern static HTTPS

Old-client surfaces must not require JavaScript, a live API, login, private
user state, arbitrary local path access, or live source probes.

If insecure/plain transports are ever introduced by a relay, they must be
read-only and public-only by default. Trust must come from future signed
manifests and checksums, not from the transport.

Trust must come from future signed manifests and checksums, not insecure
transport.

No login, private data, write action, download execution, or user-specific
state is allowed over insecure compatibility surfaces without a later explicit
security contract.
