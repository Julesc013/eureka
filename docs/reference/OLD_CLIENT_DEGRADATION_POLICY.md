# Old Client Degradation Policy

Eureka does not try to make one modern web app support every old client.
Compatibility comes from multiple read-only projections of the same resolver
truth.

Preferred fallback order:

1. current static public site for normal browsers
2. `/lite/` for old GUI browsers and low-capability HTML clients
3. `/text/` for text browsers, terminals, screen readers, and simple automation
4. `/files/` and `/data/` for file-tree clients and mirrors
5. Signed Snapshot Format v0 seed examples today, and future production signed
   snapshots for offline or TLS-limited systems
6. future local relay for systems that cannot consume modern static HTTPS

Relay Surface Design v0 now records the future local/LAN relay contract,
security/privacy defaults, protocol candidates, and unsigned operator
checklist. It does not implement a relay runtime, protocol server, network
listener, private data exposure, live-probe passthrough, or write/admin route.

Old-client surfaces must not require JavaScript, a live API, login, private
user state, arbitrary local path access, or live source probes.

If insecure/plain transports are ever introduced by a relay, they must be
read-only and public-only by default. Trust must come from future signed manifests,
future production signing policy, and checksums, not from the transport. The
current Signed Snapshot Format v0 seed example has checksums and
signature-placeholder documentation only; it has no real signing keys, no
production signatures, no executable downloads, and no public `/snapshots/`
route.

Signed Snapshot Consumer Contract v0 defines how future old-client-oriented
file-tree, text, lite HTML, relay, native, and audit consumers should read
snapshot files, validate checksums where capable, and treat v0 signatures as
placeholders. It does not implement a consumer, relay, native client,
production signing, real keys, executable downloads, live backend, or live
probes.

No login, private data, write action, download execution, or user-specific
state is allowed over insecure compatibility surfaces without a later explicit
security contract.
