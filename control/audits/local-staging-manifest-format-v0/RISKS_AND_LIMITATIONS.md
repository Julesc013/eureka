# Risks And Limitations

- The format is not a staging runtime.
- The example manifest is synthetic and committed only for validation.
- The validator performs structural checks, checksum checks, and safety checks,
  but it does not prove truth, rights clearance, malware safety, or trust.
- Future local-private manifests must use allowed ignored roots and must avoid
  committed/public path leakage.
- Future staging tooling still needs inspector, manifest path, delete/reset,
  and review gates before any runtime state is allowed.
