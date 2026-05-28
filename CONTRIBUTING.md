# Contributing

Eureka is a local-first prototype with a Python reference backend, a promoted
local product loop, read-only public-alpha foundations, and a passed
launch-candidate gate. Contributions are welcome when they preserve
auditability, boundary clarity, and honest maturity labels.

## Before Opening A Change

- Read [README.md](README.md), [AGENTS.md](AGENTS.md), and the relevant docs
  under [docs/](docs/README.md).
- Keep changes narrowly scoped to the affected control, contract, runtime, or
  surface boundary.
- Use governed contracts and packet shapes rather than hidden coupling.
- Run validators and tests that match the changed paths.
- Do not weaken safety checks, hard evals, validators, architecture checks, or
  generated-artifact guards to make a change pass.

## Safety Rules

Do not add or enable live probes, source API calls, scraping, crawling,
arbitrary URL fetching, downloads, uploads, installers, executable actions,
accounts, telemetry, model/provider calls, credentials, public mutation, or
master/public index mutation without an explicit approved milestone.

Do not commit secrets, API keys, operator tokens, private local paths, local
instance state, raw private caches, raw local indexes, raw live source
responses, full-discovery raw logs, executable payloads, installers, or
copyrighted payload dumps.

Treat pack, source, AI, search, and external-baseline claims as evidence-backed
and review-gated. Candidates, observations, and summaries are not accepted
truth.

## Testing Discipline

Use focused lanes during normal development:

```powershell
python scripts/eureka_test_select.py --changed --failed-first --json
```

Use the public-alpha gate wrapper when the change touches launch/public-alpha
posture:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --watch --clean
```

Full unittest discovery must run outside AI chat/model sessions through the
harness or CI:

```powershell
python scripts/run_full_unittest_discovery.py --out ..\eureka-test-runs\manual_full_discovery
```

## Branch And Review Posture

Current contribution intake is through repository workflow, such as issues and
pull requests. Eureka does not currently have hosted product submission,
accounts, marketplace intake, or public contribution intake behavior.

Public-alpha launch, deployment, production readiness, live metadata pilots,
native distribution, and action-layer work all require explicit review gates.

## Licensing

No root `LICENSE` file is currently present. Do not assume open-source license
terms until the repository owner or authorized legal decision-maker selects one.
See [License Selection Required](docs/operations/LICENSE_SELECTION_REQUIRED.md).
