# Local Workbench Page Hardening

LOCAL-06 makes the read-only HTML workbench operationally useful before WorkUnits, review mutation, source probes, LAN mode, or deployment exist.

## Hardened Pages

- Home shows a local status card, search form, status/API links, read-only local-only banner, and unavailable capabilities.
- Status shows instance identity, schema version, display-safe root, store status, reviewed public index status, migration state, and disabled flags.
- Search shows reviewed local result count, local index limitation, result provenance, source family, trust lane, warnings, and limitations.
- Object shows normalized fields, safe searchable text excerpt, source link, provenance references, warnings, limitations, and a safe not-found state.
- Source shows only records in the local reviewed index for the source ID and explicitly avoids a global source coverage claim.
- Absence shows checked local layers, unchecked/deferred layers, checked source references, limitations, and the non-claim that absence is not proof the artifact does not exist.

## Validation

Run:

```bash
python scripts/validate_local_workbench_page_hardening.py
python scripts/eureka_local_workbench_smoke.py --base-url http://127.0.0.1:8765 --json
```

The validator renders pages in-process, starts a loopback service smoke when safe, checks JSON API compatibility, rejects external assets and mutation controls, checks non-claim wording, and records leakage posture.

## Deferrals

WorkUnits remain deferred until LOCAL-07. Review/rebuild UI remains deferred until LOCAL-08. LAN remains deferred until LOCAL-11/LOCAL-12. F0 remains deferred until LOCAL-14.
