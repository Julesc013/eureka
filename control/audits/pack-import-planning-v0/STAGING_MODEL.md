# Staging Model

Future staging must be local, private by default, and user controlled. This
planning pack documents logical roots only; it does not create runtime staging
directories.

Suggested future logical roots:

- `.eureka-local/staged_packs/`
- `.eureka-local/quarantine/`
- `.eureka-local/import_reports/`

Staging rules:

- the staging root is selected by the user or local app profile
- staged data is private by default
- staged data is not committed to git
- staged data is never written under `site/dist`
- staged data is never written under `external`
- staged data is never part of public data by default
- staged data must be deletable and resettable
- staging reports must not leak private absolute paths into public reports
- every staged pack records pack ID, pack version, checksum, validator status,
  privacy classification, rights classification, and risk classification

Native clients may later use app-specific private cache roots, but those roots
must follow the same privacy and public-leakage rules.

