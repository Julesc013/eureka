# Next Deployment Requirements

Before any real public hosting, a separate future milestone must:

- choose a hosting target
- deploy from a reviewed commit
- configure HTTPS/TLS
- configure rate limits and abuse controls
- set environment mode to public_alpha
- keep live probes disabled unless a future gateway contract approves them
- run smoke checks after deployment
- record operator signoff
- define rollback path
- define logging and privacy posture
- review all review-required routes

Live probes must remain disabled until a future source-probe gateway contract and abuse-control posture exist.

