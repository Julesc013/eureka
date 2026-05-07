# Remaining Risks

- First real target import only; broader target-repo behavior is not proven.
- The direct Q21 importer has a broader write set than Q22 allowed, so target-scoped import was required.
- Provider/Gateway validation requires optional `core/**` files that were not imported.
- AIDE `selftest`/`test` aliases currently fail in their own temporary fixture.
- Verifier remains WARN because optional recommendation/Gateway/provider status reports are absent.
- Baseline token savings use `chars / 4`; no exact tokenizer or billing integration exists.
- The next Eureka task still needs a reviewed task-specific scope before product implementation.
