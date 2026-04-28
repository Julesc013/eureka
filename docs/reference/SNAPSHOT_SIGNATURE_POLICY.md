# Snapshot Signature Policy

Signed Snapshot Format v0 uses placeholder signature documentation only.

Current policy:

- no real signing keys
- no real private signing keys in the repository
- no production signing ceremony
- no production trust chain
- no claim that the seed example is an authentic release artifact
- no executable downloads or software mirrors

The seed example includes `SIGNATURES.README.txt` so clients can learn where
signature metadata will live later without mistaking v0 for a signed release.
It is not a production signed release.

Checksums in `CHECKSUMS.SHA256` provide deterministic integrity checks against
accidental corruption and generator drift. A checksum obtained from the same
untrusted location as the snapshot is not full authenticity proof.

Before real signed release snapshots exist, Eureka needs:

- key ownership and custody decision
- public key distribution policy
- release signing procedure
- revocation and rotation policy
- operator signoff record
- rights/security review for any future downloadable payloads

This policy does not add keys, secrets, production signatures, relay behavior,
native clients, live backend behavior, live probes, or downloads.
