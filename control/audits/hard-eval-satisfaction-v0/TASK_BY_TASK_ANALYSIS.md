# Task By Task Analysis

## `driver_inside_support_cd`

Current status: `partial`

Evidence used:

- local bundle fixture source: `local-bundle-fixtures`
- member path: `drivers/wifi/thinkpad_t42/windows2000/driver.inf`
- hardware evidence from member path and summary: ThinkPad T42 Wi-Fi
- platform evidence from member path and compatibility member:
  Windows 2000 / Windows NT 5.0
- artifact locator: INF member inside support ZIP fixture

The search expected-result check is satisfied, but the task remains overall
partial because lane placement and bad-result pattern scoring are not yet
evaluated by the runner.

## `latest_firefox_before_xp_drop`

Current status: `partial`

Evidence used:

- Internet Archive recorded fixture source:
  `internet-archive-recorded-fixtures`
- source record: `ia-firefox-xp-support-fixture`
- local bundle member: `browsers/firefox-xp-support/readme.txt`
- Windows XP compatibility/support-window evidence

Remaining gap: the fixture intentionally does not identify the exact last
compatible Firefox release or direct installer artifact. The search check is
therefore partial, not satisfied.

## `old_blue_ftp_client_xp`

Current status: `partial`

Evidence used:

- local bundle fixture source: `local-bundle-fixtures`
- source record: `windows-xp-browser-tools-bundle`
- member listing: `utilities/ftp-blue-client/readme.txt`
- Windows XP compatibility evidence
- functional trace: old blue FTP client

Remaining gap: the fixture does not prove a concrete product identity or direct
installer. The search check is partial, not satisfied.

## `win98_registry_repair`

Current status: `partial`

Evidence used:

- Internet Archive recorded fixture source:
  `internet-archive-recorded-fixtures`
- source record: `ia-win98-registry-repair-fixture`
- file listings:
  - `registry-repair/registry-repair.exe.txt`
  - `registry-repair/README-windows98.txt`
- Windows 98 compatibility evidence
- functional registry-repair description

The search expected-result check is satisfied, but the task remains overall
partial because lane placement and bad-result pattern scoring are not yet
evaluated by the runner.

## `windows_7_apps`

Current status: `partial`

Evidence used:

- Internet Archive recorded fixture source:
  `internet-archive-recorded-fixtures`
- source record: `ia-win7-portable-apps-fixture`
- file listings:
  - `portable-app-package/individual-application-installer.exe.txt`
  - `portable-app-package/README-windows7.txt`
- Windows 7 / Windows NT 6.1 compatibility evidence
- source-family visibility

The search expected-result check is satisfied, but the task remains overall
partial because lane placement and bad-result pattern scoring are not yet
evaluated by the runner.

## `article_inside_magazine_scan`

Current status: `capability_gap`

Reason: no bounded article, page-range, scan, or OCR fixture exists for the
1994 ray-tracing magazine task. This pack deliberately does not fake article
evidence.
