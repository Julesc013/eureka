# Validation Rules

`scripts/validate_contribution_pack.py` validates the example pack and any
specified pack root. It parses the manifest and JSONL files, verifies
contribution ids, allowed contribution types, proposed actions, referenced pack
records, manual observation posture, checksums, privacy/status consistency,
privacy/rights docs, private-path rejection, prohibited secret keys, raw
database/cache extension rejection, executable extension rejection, and no live
network authority.

The validator performs no upload, import, runtime review, network access,
automatic acceptance, or master-index mutation.
