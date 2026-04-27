# Query Movement

No committed v0 per-query machine output exists, so exact per-query movement is
not claimed as machine-derived history. The movement below is inferred from the
current audit output, committed expected-current-status fields, and aggregate
status movement.

## Inferred Newly Partial Queries

These query IDs are currently `partial` after previously being expected as
`source_gap` or `capability_gap`:

- `creative_ct1740_driver_windows_98`
- `driver_inf_inside_support_cd`
- `driver_thinkpad_t42_wifi_windows_2000`
- `last_opera_for_windows_2000`
- `last_winamp_for_windows_98`
- `latest_firefox_before_xp_support_ended`
- `latest_vlc_for_windows_xp`
- `mac_os_9_browser`
- `old_blue_ftp_client_xp`
- `powerpc_osx_104_browser`
- `support_cd_member_driver`
- `threecom_3c905_windows_95_driver`
- `windows_7_apps`
- `windows_7_portable_apps_archive`
- `windows_98_registry_repair`
- `windows_xp_ftp_clients`
- `windows_xp_software`

## Still Source Gaps

Representative remaining `source_gap` query IDs:

- `archived_firefox_xp_release_notes`
- `archived_microsoft_download_center_directx_90c`
- `article_ray_tracing_1994_magazine`
- `ati_rage_128_windows_98_driver`
- `dead_vendor_support_page_driver`
- `directx_90c_offline_installer_windows_98`
- `epson_scanner_windows_2000_driver`
- `last_chrome_for_windows_xp`
- `last_itunes_for_windows_xp`
- `manual_sound_blaster_ct1740`
- `old_ftp_client_blue_icon_windows_xp`
- `sound_blaster_live_ct4830_driver_windows_98`
- `thinkpad_t42_hardware_maintenance_manual`
- `visual_cpp_6_service_pack_download`
- `windows_2000_antivirus`
- `windows_98_resource_kit_pdf`

## Still Capability Gaps

Current `capability_gap` query IDs include:

- `archive_resolution_eval_runner_query`
- `archivebox_release_085_source`
- `github_cli_release_v2650_source`
- `installer_inside_iso`
- `intentionally_missing_synthetic_target`
- `missing_subject_query`
- `missing_synthetic_target_absence`
- `package_release_with_source_tarball`
- `public_alpha_status_query`

## Hard-Test Candidates

The following should become hard regression tests or hard eval satisfaction
targets before further broad source expansion:

- `driver_inside_support_cd`
- `latest_firefox_before_xp_drop`
- `old_blue_ftp_client_xp`
- `win98_registry_repair`
- `windows_7_apps`

At Delta v1 these had local results but remained `not_satisfied`; that was the
next precision gap. Hard Eval Satisfaction Pack v0 later moved them to partial.
