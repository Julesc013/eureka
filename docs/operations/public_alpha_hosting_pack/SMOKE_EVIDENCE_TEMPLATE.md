# Public Alpha Smoke Evidence Template

Do not pre-fill this template. Complete it after running the rehearsal checks.

## Rehearsal Metadata

- date/time:
- operator:
- commit SHA:
- branch status:
- working tree status:
- public-alpha mode confirmed:

## Route Inventory

- inventory path:
- inventory version:
- total route count:
- safe_public_alpha count:
- blocked_public_alpha count:
- local_dev_only count:
- review_required count:
- deferred count:

## Test Results

- `python scripts/public_alpha_smoke.py`:
- `python scripts/public_alpha_smoke.py --json`:
- `python scripts/generate_public_alpha_hosting_pack.py --check`:
- `python -m unittest discover -s runtime -t .`:
- `python -m unittest discover -s surfaces -t .`:
- `python -m unittest discover -s tests -t .`:
- `python scripts/check_architecture_boundaries.py`:
- `git diff --check`:

## Smoke Result Summary

- total checks:
- passed checks:
- failed checks:
- status endpoint result:
- private path leakage observed:
- disabled capabilities observed:

## Safe Route Samples

- route:
  result:
- route:
  result:
- route:
  result:

## Blocked Route Samples

- route:
  result:
- route:
  result:
- route:
  result:

## Known Failures

- failure:
- impact:
- owner:
- decision:

## Operator Decision

Choose one:

- pass rehearsal:
- fail rehearsal:
- blocked:

## Notes

-
