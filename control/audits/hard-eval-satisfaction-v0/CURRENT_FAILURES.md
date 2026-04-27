# Current Failures Before This Pack

Search Usefulness Audit Delta v1 recorded the archive-resolution hard eval
baseline after Old-Platform Source Coverage Expansion v0:

| status | count |
| --- | ---: |
| capability_gap | 1 |
| not_satisfied | 5 |

The baseline was progress but not success. Five hard tasks returned bounded
source-backed local candidates, but the eval runner still reported
`not_satisfied` because it only checked for older literal expected-result hint
text in top results.

## Baseline Task Shape

| task | baseline status | reason |
| --- | --- | --- |
| `article_inside_magazine_scan` | capability_gap | No bounded scan/OCR/article/page fixture exists. |
| `driver_inside_support_cd` | not_satisfied | Driver/member candidates existed, but structured member path, hardware, and platform evidence were not evaluated. |
| `latest_firefox_before_xp_drop` | not_satisfied | XP Firefox support-note candidates existed, but exact latest-version/release artifact evidence was still missing. |
| `old_blue_ftp_client_xp` | not_satisfied | XP FTP-client trace evidence existed, but concrete identity/direct installer evidence was still missing. |
| `win98_registry_repair` | not_satisfied | Registry-repair fixture evidence existed, but file-list and compatibility evidence were not evaluated as hard expected-result evidence. |
| `windows_7_apps` | not_satisfied | Windows 7 portable-app fixture evidence existed, but representation/file-list and compatibility evidence were not evaluated. |

No external baseline observations were involved.
