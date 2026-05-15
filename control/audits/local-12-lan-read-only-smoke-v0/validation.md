# Validation

LOCAL-12 validation completed:

- `git diff --check`: pass.
- JSON parsing for LOCAL-12 policies, inventories, and report: pass.
- `python scripts/eureka_lan_smoke.py --instance ./eureka-instance --host 0.0.0.0 --port 8765 --bind-lan --read-only --json`: pass with warnings.
- `python scripts/validate_local_lan_smoke.py`: pass with warnings.
- Focused LOCAL-12 tests: pass.
- `python scripts/check_architecture_boundaries.py`: pass.
- LOCAL validators from earlier queue phases: pass with warnings where compatible, fail where older validators require earlier queue pointers after LOCAL-12 advanced the queue to LOCAL-13.
- Runtime architecture leakage checks: fail on pre-existing leakage baseline; LOCAL-12 did not increase leakage.
- `python -m unittest discover -s tests -t .`: fail other. Full discovery includes the known leakage gate and broader historical discovery-lane failures.

External second-client LAN smoke was not performed in this automated run and is recorded as a limitation, not cross-device proof.
