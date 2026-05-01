# Risks And Limitations

- The redaction layer is conservative but not a full data-loss-prevention
  system.
- The inspector summarizes manifest metadata; it does not inspect pack payload
  bytes or external sources.
- Validation depends on Local Staging Manifest Format v0.
- A valid inspection does not prove truth, rights clearance, malware safety,
  public safety, or master-index acceptance.
- Real staging, delete/reset tooling, local index candidates, and contribution
  exports remain future work.
