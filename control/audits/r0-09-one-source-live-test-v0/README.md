# R0-09 One Source Live Test

This audit pack records the bounded PyPI `sampleproject` metadata live test.

The run performs one approved metadata GET only when `--live` is explicit, then carries the response through source observation, source cache, evidence ledger, review queue, reviewed public index rebuild, search, and absence reporting. No package archives are downloaded, no install or execution occurs, and no site or master index is mutated.
