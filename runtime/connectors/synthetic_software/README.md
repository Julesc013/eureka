# Synthetic Software Connector

`runtime/connectors/synthetic_software/` contains the local-only synthetic connector used to prove the bootstrap ingestion boundary.

This connector:

- reads governed synthetic fixture data from `contracts/archive/fixtures/software/`
- exposes source loading only
- does not define canonical archive truth
- does not perform trust weighting
- does not imply a real external connector strategy

