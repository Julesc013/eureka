# Vendor Update Driver Source Family Model

The `vendor_update_driver_firmware` family covers vendor update catalogs, driver catalogs, vendor support/download catalogs, firmware/update metadata, and runtime redistributable catalogs.

Connector families are planned as `vendor_update_catalog`, `driver_catalog`, `vendor_support_catalog`, and `runtime_redistributable_catalog`. These are policy families at H5-BUNDLE-01 and have no live connector runtime.

Every family member requires fixture replay, dry-run policy evaluation, endpoint or metadata allowlisting, risk review, rights posture review, output path review, no-download review, no-execution review, and scorecard review before any future expansion.
