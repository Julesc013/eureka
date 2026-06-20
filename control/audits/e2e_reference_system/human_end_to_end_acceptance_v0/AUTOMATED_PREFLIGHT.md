# Automated Preflight

Status: PASS

Automated preflight verifies that the pinned build can create and diagnose a fresh local portable instance. It does not equal human acceptance and does not fill the operator feedback form.

## Instance

- label: eureka-e2e-acceptance-v0
- root: `D:\Projects\Eureka\instances\eureka-e2e-acceptance-v0`
- posture: explicit local private path outside the repository

## Results

| Check | Command | Result |
| --- | --- | --- |
| Bootstrap | `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 bootstrap --json` | PASS |
| Bootstrap idempotence | same command repeated | PASS |
| Doctor | `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 doctor --strict --json` | PASS |
| Core oracle | `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 test --suite core --json` | PASS |
| Status | `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 status --json` | PASS |
| Serve smoke | `python scripts/eureka.py --instance ../instances/eureka-e2e-acceptance-v0 serve --mode exploration --host 127.0.0.1 --port 0 --smoke --json` | PASS |

## Key Evidence

- instance id: eureka-local-524ab24d44b65f47
- instance store count: 9
- preview index generation: preview-index-6806f12296e10452e145d4a6
- preview index records: 19
- preview index validation: PASS
- reviewed count: 0
- synthetic count: 19
- core oracle execution: e2e-eval-core-20260620T072934Z-a65a322159
- core oracle cases: 10
- core oracle gate: PASS
- serve smoke URL: `http://127.0.0.1:38003/explore`
- serve smoke endpoints: `/health`, `/status`, `/explore`, `/api/v1/explore`
- smoke server final state: stopped

## Safety Posture

- live providers enabled: false
- model/provider calls: false
- network provider calls: false
- public exposure: false
- production truth mutation: false
- reviewed/master mutation: false
- public-index mutation: false
- operator token generated during smoke: true
- operator token persisted: false
- full unittest discovery: not run
