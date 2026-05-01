# Contributing

Eureka is pre-production and prototype-stage. Contributions are welcome when
they preserve auditability, boundary clarity, and honest maturity labels.

Before opening a change:

- Read `AGENTS.md`, `README.md`, and the relevant docs under `docs/`.
- Keep changes narrowly scoped to the affected contract, control, runtime, or
  surface boundary.
- Run the validators and tests that match the changed files. For larger work,
  use `control/inventory/tests/command_matrix.json` and
  `docs/operations/TEST_AND_EVAL_LANES.md`.
- Do not weaken hard evals, validators, architecture checks, or safety guards
  to make a change pass.
- Do not add live probes, source API calls, scraping, crawling, arbitrary URL
  fetching, downloads, uploads, installers, accounts, telemetry, AI runtime, or
  credentials without an explicit approved milestone.
- Do not commit secrets, API keys, private local paths, copyrighted payload
  dumps, executable payloads, installer files, raw private caches, or raw local
  indexes.
- Treat pack, source, AI, and external-baseline claims as evidence-backed and
  candidate-gated. Validation is not import, staging, acceptance, truth,
  rights clearance, or malware safety.

Current contribution intake is through the repository workflow, such as issues
and pull requests. Eureka does not have hosted product submission, account, or
public contribution intake behavior.

Root governance documents are minimal pre-production placeholders. Full legal,
security, privacy, takedown, and hosted-service policies remain future
operator/legal work.
