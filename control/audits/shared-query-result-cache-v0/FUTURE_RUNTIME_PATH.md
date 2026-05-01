# Future Runtime Path

Future cache runtime work must wait for a later milestone. It should:

- preserve raw query retention default `none`
- apply privacy and poisoning filters before writes
- bind cache entries to public index snapshot and source status
- invalidate on public index, source, contract, rights, or safety changes
- keep cached absence scoped
- avoid master-index mutation
- remain separate from miss ledger, search needs, probe queue, and candidate
  index until those contracts exist

P61 should define Search Miss Ledger v0 next.
