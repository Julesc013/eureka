# Connector Interface Model

Source OS separates four ideas:

- source: a governed external or local source record
- connector: code or policy that can parse source-shaped data
- capability: a descriptive statement about what might be possible
- policy: the gate that decides what is allowed

H0-BUNDLE-02 adds the generic connector layer so future source families do not
become one-off integrations. IA remains the reference pattern, but the generic
contracts can also cover package registries, WARC/CDX, OAI-PMH, IIIF, HTML
catalogs, directory listings, local source manifests, and restricted manifests.

No new live source access is enabled by this model.
