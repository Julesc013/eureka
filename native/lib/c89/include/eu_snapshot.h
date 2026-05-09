#ifndef EU_SNAPSHOT_H
#define EU_SNAPSHOT_H

#include <stddef.h>
#include "eu_status.h"

#ifdef __cplusplus
extern "C" {
#endif

int eu_snapshot_has_manifest_marker(const char *text, size_t text_len);
int eu_snapshot_has_record_marker(const char *text, size_t text_len);
int eu_snapshot_has_no_claims_marker(const char *text, size_t text_len);
eu_status_code eu_snapshot_status_from_text(const char *text, size_t text_len, char *dest, size_t dest_size);

#ifdef __cplusplus
}
#endif

#endif
