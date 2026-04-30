# Validation Pipeline

Future import must run validation before any staging or inspection.

Required pipeline:

1. Identify the explicit pack path selected by the user.
2. Identify pack type from its manifest name and schema version.
3. Parse the manifest.
4. Validate the schema and required manifest fields.
5. Validate checksums.
6. Parse declared JSON and JSONL files.
7. Validate privacy/status consistency.
8. Scan for forbidden fields and private absolute paths.
9. Scan for executable payloads, raw databases, and cache dumps.
10. Validate rights/access or privacy/rights documents.
11. Classify privacy, rights, and risk posture.
12. Produce an import report.
13. Stage or reject according to explicit mode.
14. Never mutate canonical source, evidence, index, search, or master-index
    records by default.

Existing validators are the first building blocks:

- `python scripts/validate_source_pack.py`
- `python scripts/validate_evidence_pack.py`
- `python scripts/validate_index_pack.py`
- `python scripts/validate_contribution_pack.py`
- `python scripts/validate_master_index_review_queue.py`

The next recommended milestone is Pack Import Validator Aggregator v0, which
should call the appropriate validators through one safe command without adding
import runtime behavior.

