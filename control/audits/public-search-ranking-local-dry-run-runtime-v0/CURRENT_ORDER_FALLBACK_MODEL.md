# Current-Order Fallback Model

Current public search order is preserved outside this dry-run.

Fallback is used when:

- input requires current order
- required factor data is missing
- policy rejects ranking
- explanation generation is missing
- strict mode is requested and fallback would otherwise be needed

Dry-run proposed order is report-only. Invalid input can fail in strict mode, but no public search runtime or index mutation occurs.

