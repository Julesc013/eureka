# E2E Reference ID And Hash Profile

## Canonical Algorithm

New deterministic semantic IDs should use:

```text
<semantic-type>:<namespace>:<short-slug-or-short-hash>
```

The semantic hash algorithm is SHA-256 over canonical JSON.

## Canonical Serialization

Canonical JSON means:

- UTF-8;
- sorted object keys;
- no insignificant whitespace;
- normalized arrays when order is not semantic;
- stable enum/string values;
- timestamps excluded from semantic identity unless the time is the identity.

## Timestamp Posture

`created_at`, `observed_at`, `decided_at`, `generated_at`, and `occurred_at`
must not destabilize semantic IDs unless a specific contract says the timestamp
is part of identity.

## Namespace Policy

Namespaces must prevent cross-domain collisions:

```text
synthetic:e2e-reference
source:internet_archive_metadata
review:local
snapshot:local
```

Legacy IDs remain resolvable through aliases or reference maps. No bulk ID
migration occurs in `E2E-REFERENCE-CONTRACT-00`.

