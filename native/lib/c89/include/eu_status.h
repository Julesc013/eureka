#ifndef EU_STATUS_H
#define EU_STATUS_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum eu_status_code {
    EU_STATUS_OK = 0,
    EU_STATUS_NULL_ARGUMENT = 1,
    EU_STATUS_BUFFER_TOO_SMALL = 2,
    EU_STATUS_NOT_FOUND = 3,
    EU_STATUS_INVALID_ARGUMENT = 4,
    EU_STATUS_BOUNDARY_VIOLATION = 5
} eu_status_code;

int eu_status_is_ok(eu_status_code code);
const char *eu_status_name(eu_status_code code);

#ifdef __cplusplus
}
#endif

#endif
