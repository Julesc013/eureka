# Public Index Store Summary

R0-08 adds `runtime/public_index`, a standard-library SQLite runtime package for a local reviewed public index.

The store contains reviewed records, rebuild metadata, search terms, source references, evidence references, and review references. It supports in-memory tests and explicit file-backed databases. It refuses product, private, and generated site output roots for runtime writes.
