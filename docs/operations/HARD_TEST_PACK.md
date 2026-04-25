# Hard Test Pack v0

Hard Test Pack v0 converts the highest-risk findings from the Comprehensive Test/Eval Operating Layer and Repo Audit v0 into enforceable `unittest` guardrails.

This is a quality layer, not product behavior. It does not add connectors, retrieval semantics, Rust runtime behavior, public hosting, deployment infrastructure, or production-readiness claims.

## Required Lane

Run the hardening lane with:

```bash
python -m unittest discover -s tests/hardening -t .
```

The lane is required for repo-wide governance, eval, public-alpha, parity, and README/docs changes that could silently weaken claims or drift from current command behavior.

## Guarded Risks

Hard Test Pack v0 protects against:

- weakening the archive-resolution hard eval packet
- shrinking or softening the search usefulness query pack
- fabricating Google or Internet Archive baseline observations
- leaking private local paths through public-alpha status or blocked responses
- route inventory drift from web/API route policy
- README commands drifting away from real scripts
- local documentation links breaking
- Python oracle golden outputs drifting from the generator
- Rust parity scaffolding being presented as the active backend
- source placeholders being described as implemented connectors
- resolution memory storing private roots or user/account behavior fields
- AIDE queue, command matrix, and test registry inconsistency

## Required vs Advisory

The Python hardening tests are required when their lane is invoked. Cargo remains optional because Rust tooling is not guaranteed in every environment.

The tests intentionally use local deterministic commands and static repo inspection. They do not make network calls and do not start persistent servers.

## Relationship To The Audit Pack

The comprehensive audit pack proposed many future hard tests. Hard Test Pack v0 implements the first enforceable subset. Future audits should add new hard tests when a risk is concrete enough to fail deterministically.

## What This Does Not Test

Hard Test Pack v0 does not prove:

- global search relevance
- production hosting readiness
- auth, TLS, accounts, or abuse controls
- live source coverage
- ranking, fuzzy, vector, LLM, or semantic retrieval quality
- Rust replacement readiness

Those remain future work governed by separate eval, parity, public-alpha, and source-coverage milestones.
