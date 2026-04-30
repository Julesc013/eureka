# Source-Family Impact

Source Expansion v2 contributed six recorded fixture-only families.

| Source ID | Source family | Fixture status | Queries helped | Remaining limitations |
| --- | --- | --- | --- | --- |
| wayback-memento-recorded-fixtures | wayback_memento_recorded | recorded_fixture_only | archived Firefox XP notes; DirectX 9.0c page; Creative Labs page; Netscape page | No live capture lookup, no URL fetch, no guarantee that captures exist outside fixtures |
| software-heritage-recorded-fixtures | software_heritage_recorded | recorded_fixture_only | software heritage source snapshot old project | SWHID-like provenance only; no live source-code archive calls |
| sourceforge-recorded-fixtures | sourceforge_recorded | recorded_fixture_only | classic Windows file transfer app blue globe | Release/project metadata only; no live project lookup or downloads |
| package-registry-recorded-fixtures | package_registry_recorded | recorded_fixture_only | Visual C++ 6 service pack download/readme | Package/version metadata only; no package registry calls or install actions |
| manual-document-recorded-fixtures | manual_document_recorded | recorded_fixture_only | Sound Blaster manuals; ThinkPad manual; Windows 98 resource kit PDF | Metadata and tiny notes only; no copied manuals or OCR corpus |
| review-description-recorded-fixtures | review_description_recorded | recorded_fixture_only | Windows 2000 antivirus; last Chrome/iTunes for XP | Subjective compatibility notes only; not canonical compatibility truth |

Existing fixture families also continue to carry useful coverage:

- `synthetic_fixture`
- `github_releases`
- `internet_archive_recorded`
- `local_bundle_fixtures`
- `article_scan_recorded`

The next source work should define governed Source Pack and Evidence Pack contracts so fixture families can scale without muddying source posture, evidence provenance, or action policy.

