# Public Alpha Security Model

The public alpha security model is deliberately narrow: serve reviewed snapshot
and relay projections through read-only routes while keeping risky behavior
disabled.

## Required Controls

- Security headers: `Content-Security-Policy`, `Referrer-Policy`,
  `X-Content-Type-Options`, `X-Frame-Options`, `Permissions-Policy`, and
  `Cross-Origin-Opener-Policy`.
- CSP baseline: default deny, allow same-origin scripts and styles only when the
  serving mode requires them, and never allow inline secrets.
- API methods: `GET` and `HEAD` only for public alpha routes.
- Request controls: request size limits, anonymous per-IP rate limits, and burst
  protection before any public launch.
- Logging: redact operator tokens, credentials, raw query payloads, and any raw
  live source response. Raw query retention is disabled by default.

## Disabled Behavior

Public mutation, live source fanout, downloads, uploads, extraction,
model/provider calls, accounts, deployment, production readiness claims, and
public launch readiness claims are all false in this readiness baseline.
