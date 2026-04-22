# Bounded Representations

This package holds Eureka's first bounded representation/access-path seam.

It is intentionally small:

- it describes known representations and access paths for one resolved target
- it does not define a final packaging, download, install, or restore model
- it does not select one representation as the single canonical truth

The current summary shape is designed to be easy to inspect and safe to carry
through normalize, exact resolution, manifest/bundle export, and surface
projection layers.
