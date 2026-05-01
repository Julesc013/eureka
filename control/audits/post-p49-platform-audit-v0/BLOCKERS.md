# Blockers

Concrete blockers:

- GitHub Pages deployment evidence is `blocked`: recorded current-head workflow failed at `actions/configure-pages@v5`; no Pages artifact or deployment URL exists.
- External baseline comparison is `blocked`: 192 global slots are pending and 0 are observed.
- Cargo workspace checks are `blocked`: Cargo is unavailable in PATH.
- Hosted public search is `operator_gated`: no deployment config, provider, ops controls, or deployment evidence exists.
- Live connectors are `approval_gated`: live probe gateway is contract-only and disabled.
- Query intelligence is `planning_only`/`deferred`: no query observation contract, miss ledger, search need record, shared cache, probe queue, candidate index, or promotion policy exists.
- Root community/security docs are `blocked` or `deferred`: `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md` are absent.
- Individual pack validator command drift exists: source/evidence/index/contribution validators do not accept the requested `--all-examples` flag, though their supported default/example forms and aggregate validator pass.
