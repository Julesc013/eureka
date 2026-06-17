# License Selection Decision

Task: `LICENSE-SELECTION-DECISION-00`

## Decision

Eureka uses a custom restricted source-viewing license:

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

## Rationale

The project should be visible for inspection, study, security review, and
private local evaluation without granting open-source reuse, redistribution,
commercial use, hosted service operation, incorporation into other projects, or
model-training reuse.

The license is inspired by the Dominium restricted source-viewing posture but
tailored to Eureka's docs, eval fixtures, source registry records, generated
artifacts, public-alpha operations, third-party material references,
contribution workflow, and future hosted-service plans.

## Files

- [LICENSE.md](../../LICENSE.md)
- [LICENSE-SUMMARY.md](../../LICENSE-SUMMARY.md)
- [NOTICE.md](../../NOTICE.md)
- [License posture note](../operations/LICENSE_SELECTION_REQUIRED.md)

## Non-Claims

- Eureka is not open source.
- Eureka is not production-ready.
- Eureka is not publicly launched.
- The license does not authorize public hosting, public APIs, public Workbench
  exposure, public live source fanout, downloads/uploads, commercial use, or
  redistribution.
- Third-party materials remain under their own rights, terms, and laws.
