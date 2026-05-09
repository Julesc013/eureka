#ifndef EU_RELAY_H
#define EU_RELAY_H

#include <stddef.h>
#include "eu_status.h"

#ifdef __cplusplus
extern "C" {
#endif

int eu_relay_status_is_readonly(const char *text, size_t text_len);
int eu_relay_status_is_loopback_only(const char *text, size_t text_len);
int eu_relay_status_blocks_live_access(const char *text, size_t text_len);
eu_status_code eu_relay_status_from_text(const char *text, size_t text_len, char *dest, size_t dest_size);

#ifdef __cplusplus
}
#endif

#endif
