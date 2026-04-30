# Contract Summary

Index Pack Contract v0 defines a portable summary-only pack for describing an
index build, source coverage, field coverage, query examples, and public-safe
record summaries.

The contract treats index records as coverage summaries, not canonical proof.
It keeps raw databases, raw local caches, private paths, source payloads,
executables, installers, live fetch authority, and master-index acceptance out
of scope.

Primary artifacts:

- `contracts/packs/index_pack.v0.json`
- `docs/reference/INDEX_PACK_CONTRACT.md`
- `examples/index_packs/minimal_index_pack_v0/`
- `scripts/validate_index_pack.py`
- `tests/scripts/test_validate_index_pack.py`
- `tests/operations/test_index_pack_contract.py`
