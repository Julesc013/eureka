# Fingerprint And Normalization Model

Normalized query text is the low-risk basis for grouping. The example normalizes
`windows 7 apps` to lowercase tokens and public-safe terms.

Fingerprints use SHA-256, are non-reversible, and include no salt value in
committed examples. Future hosted systems may choose a deployment-specific
salt, but P59 does not implement any hosted storage or runtime.
