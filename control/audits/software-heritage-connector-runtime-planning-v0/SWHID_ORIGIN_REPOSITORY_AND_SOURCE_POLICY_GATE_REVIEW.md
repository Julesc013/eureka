# SWHID, Origin, Repository, And Source Policy Gate Review

The future connector requires reviewed identity provenance before any live metadata request.

Required gates:

- SWHID policy review is pending.
- Origin URL policy review is pending.
- Repository identity policy review is pending.
- Software Heritage API/source policy review is pending.
- Operator approval is pending.

The future runtime must reject raw public query parameters, private repositories, credentialed repositories, local repository paths, localhost URLs, file URLs, uploaded files, arbitrary URLs, and unreviewed origin URLs. It does not fabricate Software Heritage metadata or real SWHIDs for real objects.
