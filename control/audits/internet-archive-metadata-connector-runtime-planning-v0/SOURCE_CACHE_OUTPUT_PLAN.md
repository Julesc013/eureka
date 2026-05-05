# Source Cache Output Plan

Future source-cache record kinds:

- `internet_archive_item_metadata_summary`.
- `internet_archive_file_listing_metadata_summary`.
- `internet_archive_collection_metadata_summary`.
- `internet_archive_availability_summary`.

Future constraints:

- Metadata summaries only.
- No raw payload dumps.
- No file downloads.
- No executable payloads.
- No private data.
- Checksum/fixity fields may be summarized when present in metadata only.
- Source attribution required.
- Freshness/invalidation policy required.
- Source policy ref required.
- Rate-limit/response metadata summary only.

P87 writes no source-cache records.
