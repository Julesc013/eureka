# License Selection Decision Report

Task: `LICENSE-SELECTION-DECISION-00`

Status: `PASS_WITH_WARNINGS`

## Selected License

```text
Eureka Temporal Object Resolver - Restricted Source Viewing License
Version 0.1
LicenseRef-Eureka-RSVL-0.1
```

## Classification

- source-available
- restricted
- non-open-source
- non-commercial
- no redistribution
- no public service hosting
- personal/local evaluation only

## Summary

This task selects a custom restricted source-viewing license for Eureka. It is
inspired by the Dominium restriction model but tailored for Eureka's docs,
schemas, eval fixtures, source records, generated outputs, public-alpha
operations, third-party/public-source references, contribution workflow, and
future hosted-service plans.

## Files Added

- `LICENSE.md`
- `LICENSE-SUMMARY.md`
- `NOTICE.md`
- `docs/planning/LICENSE_SELECTION_DECISION.md`

## Files Updated

- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/operations/LICENSE_SELECTION_REQUIRED.md`
- `docs/README.md`
- `docs/STATUS.md`
- `tests/docs/test_public_docs.py`

## Key Terms

- Viewing, private study, security review, compatibility evaluation, and private
  local evaluation are allowed.
- Short public-doc quotation with attribution is allowed for commentary, review,
  citation, and issue discussion.
- GitHub forks are allowed only for review, issue discussion, and pull request
  submission through the official workflow.
- Contributions grant the Author broad rights to use, modify, sublicense,
  relicense, and incorporate submitted material.
- Redistribution, public hosting, commercial/professional/institutional use,
  incorporation, model-training reuse, and competing services are prohibited
  without written permission.
- Third-party materials remain subject to their own rights, terms, and laws.

## Non-Claims

- Eureka is not open source.
- Eureka is not production-ready.
- Eureka is not publicly launched.
- The license does not authorize public hosting, public APIs, public Workbench
  exposure, public live source fanout, downloads/uploads, commercial use, or
  redistribution.

## Validation

- `python -m json.tool control/audits/public_alpha/LICENSE_SELECTION_DECISION_REPORT.json`: PASS
- `python -m unittest tests.docs.test_public_docs -v`: PASS, 5 tests
- `git diff --check`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: WARN before commit because the new audit report files were uncommitted `audit_generated` artifacts
- `python scripts/validate_public_alpha_readonly.py`: PASS
- `python scripts/validate_snapshot_relay.py`: PASS
- `python scripts/validate_public_alpha_hosting_readiness.py`: PASS
- `python scripts/validate_public_alpha_launch_candidate.py`: PASS
- `python scripts/public_alpha_smoke.py --json`: PASS, 18 checks
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS

Full unittest discovery was not run and is not claimed.

## Warning

This is a custom restrictive license. It should be reviewed by qualified
counsel before anyone relies on it for high-stakes legal decisions.
