# Selected Wedges

## Primary Wedge: Old-Platform-Compatible Software Search

Definition: queries where the user is trying to find software, drivers, tools, or last-compatible releases for older operating systems or hardware.

Representative query IDs:

- `windows_7_apps`
- `query_planner_windows_7_apps`
- `windows_xp_software`
- `windows_xp_ftp_clients`
- `windows_98_registry_repair`
- `windows_2000_antivirus`
- `latest_firefox_before_xp_support_ended`
- `latest_vlc_for_windows_xp`
- `last_opera_for_windows_2000`
- `driver_thinkpad_t42_wifi_windows_2000`
- `old_blue_ftp_client_xp`
- `mac_os_9_browser`
- `powerpc_osx_104_browser`

Representative platform language: Windows 7 / NT 6.1, Windows XP, Windows 2000, Windows 98, Mac OS 9, and PowerPC Mac OS X 10.4.

Desired useful result:

- specific software product, release, driver, or tool
- compatibility evidence for the target platform
- source/provenance
- representation or access path
- direct artifact or member when available
- explicit absence explanation when not found

Do not return:

- generic OS ISOs
- parent collections with no member or artifact trace
- compatibility guesses without evidence
- modern incompatible releases as if they satisfy old-platform constraints

Why selected: it combines the largest source/planner/compatibility failure families with an obvious user value story. It also lets Eureka show that it is an object resolver rather than a flat keyword search surface.

## Secondary Wedge: Member-Level Discovery Inside Bundles

Definition: queries where the useful result is inside a larger package, support disc, ISO, ZIP, scan, WARC/WACZ, or source archive.

Representative query IDs:

- `driver_inf_inside_support_cd`
- `support_cd_member_driver`
- `installer_inside_iso`
- `readme_inside_old_zip`
- `directx_90c_offline_installer_windows_98`
- `visual_cpp_6_service_pack_download`
- `article_ray_tracing_1994_magazine`
- `pc_magazine_july_1994_ray_tracing`
- `archivebox_release_085_source`

Desired useful result:

- smallest actionable member where evidence supports it
- parent lineage preserved
- member target refs distinct from parent container refs
- member path/hash/content type
- source and evidence carried to the member
- result cards and action routing that distinguish parent and member

Do not claim broad implementation today. Current decomposition/member support is bounded and fixture-driven.

Why selected: it is central to Eureka's doctrine of returning the smallest actionable unit and it supports multiple query families that Google-like flat search often makes tedious.
