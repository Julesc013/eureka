# PUBLIC-ALPHA-READONLY-00

This task adds the local public alpha read-only foundation.

Implemented scope:

- reviewed snapshot search at `/api/v1/alpha/search` and `/alpha`
- public object packets from reviewed snapshot records
- public source, evidence, absence, and known-need summary packets
- relay-backed API projection metadata
- public-alpha web projection for local review

Boundaries:

- no deployment
- no production or public launch readiness claim
- no live source fanout
- no arbitrary URL fetch
- no downloads, uploads, installs, execution, extraction, or model/provider calls
- no public index, master index, instance state, raw log, or raw live response mutation

This is a local runtime foundation only. Absence means “not present in the
current reviewed snapshot,” not “does not exist.”
