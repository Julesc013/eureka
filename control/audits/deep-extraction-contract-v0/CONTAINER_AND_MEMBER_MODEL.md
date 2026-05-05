# Container And Member Model

`target_ref` supports reviewed/public-safe future references such as public index documents, object page records, future source-cache records, evidence/source pack records, pack members, static fixtures, synthetic examples, or unknown targets.

`container_hints` and `container_summary` cover ZIP, TAR, GZIP, 7z, ISO, disk images, installers, package archives, wheels, sdists, npm tarballs, WARC, WACZ, PDF, scanned volumes, source bundles, repository snapshots, and unknown containers.

`member_summaries` list logical public-safe member paths only. Members can be files, directories, manifests, metadata records, capture records, OCR layers, text segments, images, executables, installer members, nested archives, source files, or unknowns.

Member paths must not be absolute, path-traversal, private cache roots, home/user paths, arbitrary URLs, uploaded private names, or local filesystem roots. No raw member payloads are included.
