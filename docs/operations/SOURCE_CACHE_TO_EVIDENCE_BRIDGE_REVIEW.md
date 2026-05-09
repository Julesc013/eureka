# Source Cache To Evidence Bridge Review

Bridge output is local review material. A reviewer may inspect the mapped evidence candidate, its source cache lineage, limitations, policy status, and warnings before deciding whether later work should route it to candidate store review, evidence pack review, or rejection.

## Required Gates

- Review before candidate-store use
- Review before public index use
- Review before pack export
- Review before master-index mutation
- Review before rights claims
- Review before malware-safety claims
- Review before installability claims

Automatic evidence acceptance, public index use, master-index mutation, rights clearance, malware safety, and installability verification remain disabled.

## Review Checklist

- Confirm the input is a committed source cache record or fixture.
- Confirm no live source access occurred.
- Confirm provenance points to the source cache record.
- Confirm limitations were preserved.
- Confirm generated evidence candidates remain unaccepted.
- Confirm policy-blocked inputs remain blocked.
- Confirm no public truth or master-index mutation is claimed.

## Validation

```bash
python scripts/validate_source_cache_to_evidence_bridge.py
python scripts/bridge_source_cache_to_evidence.py --input examples/source_cache_records/source_metadata_record_v0.json --check
python -m unittest tests.runtime.test_source_cache_to_evidence_bridge tests.operations.test_source_cache_to_evidence_bridge_scripts
```
