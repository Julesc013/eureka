#ifndef EU_ACTION_H
#define EU_ACTION_H

#include <stddef.h>
#include "eu_status.h"

#ifdef __cplusplus
extern "C" {
#endif

int eu_action_manifest_is_safe_current(const char *text, size_t text_len);
int eu_action_manifest_is_blocked(const char *text, size_t text_len);
int eu_action_manifest_blocks_execution(const char *text, size_t text_len);
eu_status_code eu_action_family_from_text(const char *text, size_t text_len, char *dest, size_t dest_size);

#ifdef __cplusplus
}
#endif

#endif
