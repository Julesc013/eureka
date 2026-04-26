# Wedge Delta

## Selected Wedges

Primary wedge: old-platform-compatible software search.

Secondary wedge: member-level discovery inside bundles.

## Old-Platform-Compatible Software Search

Representative query IDs:

- `windows_7_apps`
- `windows_7_portable_apps_archive`
- `windows_xp_software`
- `windows_xp_ftp_clients`
- `windows_98_registry_repair`
- `windows_2000_antivirus`
- `mac_os_9_browser`
- `powerpc_osx_104_browser`
- `latest_firefox_before_xp_support_ended`
- `latest_vlc_for_windows_xp`
- `last_chrome_for_windows_xp`
- `last_opera_for_windows_2000`
- `last_winamp_for_windows_98`
- `last_itunes_for_windows_xp`
- `driver_thinkpad_t42_wifi_windows_2000`
- `creative_ct1740_driver_windows_98`
- `sound_blaster_live_ct4830_driver_windows_98`
- `ati_rage_128_windows_98_driver`
- `threecom_3c905_windows_95_driver`
- `epson_scanner_windows_2000_driver`
- `old_blue_ftp_client_xp`
- `old_ftp_client_blue_icon_windows_xp`
- `classic_windows_file_transfer_blue_globe`

Current observed shape:

- `windows_xp_software` is now `partial`.
- `latest_firefox_before_xp_support_ended` is now `partial`.
- many Windows 7, Windows 98, Windows 2000, Mac OS 9, PowerPC Mac OS X, and
  driver/hardware queries remain `source_gap`.
- planner output now carries more useful platform, temporal, hardware,
  representation, and suppression hints, but the current corpus still lacks
  enough real recorded source material.

Improvement drivers:

- Source Coverage and Capability Model v0 made source depth and posture
  explicit.
- Real Source Coverage Pack v0 added the first IA-like and local bundle
  fixture material.
- Old-Platform Software Planner Pack v0 improved platform-as-constraint and
  latest-compatible/driver intent.
- Compatibility Evidence Pack v0 made fixture-backed platform evidence visible.

Remaining blockers:

- source_coverage_gap
- compatibility_evidence_gap
- representation_gap
- planner_gap for query families not yet fully interpreted
- live_source_gap for future recorded/live source families

## Member-Level Discovery Inside Bundles

Representative query IDs:

- `driver_inf_inside_support_cd`
- `support_cd_member_driver`
- `readme_inside_old_zip`
- `installer_inside_iso`
- `directx_90c_offline_installer_windows_98`
- `visual_cpp_6_service_pack_download`
- `synthetic_package_member_readme`

Current observed shape:

- `synthetic_package_member_readme` remains `covered`.
- `driver_inf_inside_support_cd` is now `partial`.
- `support_cd_member_driver` is now `partial`.
- `readme_inside_old_zip` and `installer_inside_iso` remain capability-bound
  because broad archive/member extraction is not implemented.
- DirectX and Visual C++ service-pack queries remain mostly source-bound.

Improvement drivers:

- Local bundle fixtures provide committed member paths.
- Member-Level Synthetic Records v0 produces deterministic member target refs.
- Result lanes and user-cost annotations explain why inner members can be more
  useful than parent bundles.
- Compatibility evidence can attach to member paths such as Windows 2000 driver
  paths and Windows 7 compatibility notes.

Remaining blockers:

- member_access_gap for formats and sources outside the bounded ZIP fixture
  seam
- decomposition_gap for ISO, scan, WARC/WACZ, and package formats
- representation_gap where parent source records lack item-file or member
  listings
- source_coverage_gap for real support media and old package collections

## Wedge Verdict

The selected wedges were the right first focus because they produced measurable
partial-result movement without hiding limits. The next source expansion should
target old-platform release, driver, support-media, utility, and manual
fixtures so the planner/member/compatibility seams have more evidence to use.
