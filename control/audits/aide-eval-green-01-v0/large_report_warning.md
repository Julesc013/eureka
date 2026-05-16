# Large Report Warning

Before remediation, `.aide/reports/file-quality-ledger.json` was 56,106,467
bytes, above the 50 MB warning threshold.

The ledger now uses compact JSON serialization and is below the threshold
without removing record data.

