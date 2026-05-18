# Boundary Report

IA-02 boundary result:

- live source call attempted: true
- source probe attempted: true
- source-cache write: false
- evidence write: false
- candidate index mutation: false
- reviewed index mutation: false
- master index mutation: false
- download: false
- upload: false
- extraction: false
- model/provider call: false
- deployment: false
- production readiness claim: false
- public launch claim: false

The only failure was the local TLS certificate verification failure before IA
returned an HTTP response.
