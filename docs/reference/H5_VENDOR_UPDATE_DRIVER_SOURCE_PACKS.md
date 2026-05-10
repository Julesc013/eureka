# H5 Vendor Update Driver Source Packs

H5 extends Source OS policy structure to official vendor/update/driver/firmware and runtime redistributable metadata sources. The current state is policy-pack-only: source records, source pack manifests, policy packs, coverage previews, and scorecard previews exist so H5-BUNDLE-02 can add fixture runtimes.

The source family is `vendor_update_driver_firmware`. It includes Microsoft Download Center, Microsoft Update Catalog, Microsoft runtime redistributables, Apple software download and update metadata, NVIDIA/AMD/Intel driver metadata, Dell/HP/Lenovo/ASUS/Acer support metadata, and generic vendor/runtime catalogs.

Current H5 packs allow only policy inspection, fixture planning, coverage previews, scorecard previews, and candidate mapping plans. They do not allow live access, catalog fetches, downloads, installer execution, vendor tools, package managers, firmware flashing, public index mutation, master index mutation, or truth acceptance.
