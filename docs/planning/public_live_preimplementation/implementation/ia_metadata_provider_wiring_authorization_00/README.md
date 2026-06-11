# IA Metadata Provider Wiring Authorization 00

Task: `IA-METADATA-PROVIDER-WIRING-AUTHORIZATION-00`

This package authorizes the bounded task:

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
```

The authorization is narrow. It allows only fixture-backed IA metadata provider
smoke work through the governed resolution-run fallback seam. It does not return
external artifact evidence, does not resolve the hardware-details blocker, does
not launch public alpha, and does not promote `dev -> main`.

IA metadata output is candidate/source-observation support only.
