#ifndef EU_STRING_H
#define EU_STRING_H

#include <stddef.h>
#include "eu_status.h"

#ifdef __cplusplus
extern "C" {
#endif

size_t eu_strnlen_c89(const char *text, size_t max_len);
int eu_contains_token(const char *text, size_t text_len, const char *token);
eu_status_code eu_copy_string(char *dest, size_t dest_size, const char *src);

#ifdef __cplusplus
}
#endif

#endif
