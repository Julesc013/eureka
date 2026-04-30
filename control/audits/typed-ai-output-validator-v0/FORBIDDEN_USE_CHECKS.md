# Forbidden Use Checks

Every output must prohibit:

- `canonical_truth`
- `rights_clearance`
- `malware_safety`
- `automatic_acceptance`

The validator also rejects secret-like fields, API-key-like values, private
absolute paths in public-safe output, positive generated-text claims about
rights clearance, malware safety, canonical truth, or automatic acceptance, and
structured claim values that attempt to turn those authorities on.
