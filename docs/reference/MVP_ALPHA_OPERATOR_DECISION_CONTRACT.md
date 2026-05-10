# MVP Alpha Operator Decision Contract

Defines the unsigned decision request record, available decision options, evidence references, and no-deploy boundary. Current records keep explicit operator approval, launch allowed, and deployment allowed set to false.

## Current Boundary

- Operator signoff is required and absent.
- Deployment, hosting provider calls, DNS changes, public bind, generated site output mutation, downloads, uploads, accounts, telemetry, public relay, live source fanout, source sync, public index mutation, and master index mutation remain forbidden.
- The review does not establish rights clearance, malware safety, installability, production readiness, or public launch.

## Validation

- `python scripts/validate_mvp_alpha_operator_review.py`
- `python scripts/check_mvp_alpha_operator_signoff.py --input examples/audits/mvp_alpha_operator/operator_signoff_packet_unsigned_v0.json --check`
- `python scripts/check_mvp_alpha_public_claims.py --input examples/audits/mvp_alpha_operator --check`
