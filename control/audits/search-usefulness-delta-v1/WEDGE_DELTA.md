# Wedge Delta

## Primary Wedge: Old-Platform-Compatible Software Search

The old-platform wedge improved substantially in the local audit. The following
query IDs are now `partial` with source-backed local results:

- `windows_7_apps`
- `windows_7_portable_apps_archive`
- `windows_98_registry_repair`
- `windows_xp_software`
- `windows_xp_ftp_clients`
- `latest_firefox_before_xp_support_ended`
- `latest_vlc_for_windows_xp`
- `last_opera_for_windows_2000`
- `last_winamp_for_windows_98`
- `mac_os_9_browser`
- `powerpc_osx_104_browser`
- `creative_ct1740_driver_windows_98`
- `driver_thinkpad_t42_wifi_windows_2000`
- `threecom_3c905_windows_95_driver`
- `old_blue_ftp_client_xp`

These improvements are driven by committed Internet-Archive-shaped fixtures and
local bundle fixture members. They are not live Internet Archive results and
not external search observations.

## Secondary Wedge: Member-Level Discovery Inside Bundles

Member-level discovery improved where bounded local bundle fixtures exist:

- `driver_inf_inside_support_cd` is `partial`.
- `support_cd_member_driver` is `partial`.
- `readme_inside_old_zip` remains `partial`.

The current system can expose member paths, parent lineage, source ids, member
target refs, lane/user-cost annotations, and compatibility evidence for bounded
fixture-backed members. It still does not implement broad archive extraction or
arbitrary local filesystem ingestion.

## Still Blocked

Source gaps remain for many old-platform query families:

- web-archive dead-link queries
- article-inside-scan queries
- ATI Rage 128 and Sound Blaster Live driver queries
- manual/documentation queries
- Visual C++ 6 package/member queries
- Windows 2000 antivirus
- old Mac compression utility
- old FTP client blue-icon identity query

The wedge now has enough fixture-backed partial evidence to justify hard-eval
satisfaction and result-refinement work, but not enough to claim broad
real-world recall.
