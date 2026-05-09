# Validation

## Completed

- `python scripts/validate_relay_runtime.py`: PASS
- Relay JSON contract/policy syntax checks: PASS
- Relay script check mode and rendering checks: PASS
- Focused relay unit tests: PASS
- `python -m unittest discover -s tests -t .`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- Existing D/J/I/G/F/H/core validators: PASS
- AIDE Lite doctor/validate/test/selftest/eval/review-pack/adapter checks: PASS, with `verify` WARN-only and zero errors.

The relay validator checks JSON syntax, policy syntax, examples, runtime module
imports without starting a server, check-mode scripts, unsafe route/method
blocking, public bind rejection, forbidden output roots, boundary claims, and
absence of private local roots.
