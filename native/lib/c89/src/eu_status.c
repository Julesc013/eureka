#include "eu_status.h"

int eu_status_is_ok(eu_status_code code)
{
    return code == EU_STATUS_OK;
}

const char *eu_status_name(eu_status_code code)
{
    switch (code) {
    case EU_STATUS_OK:
        return "ok";
    case EU_STATUS_NULL_ARGUMENT:
        return "null_argument";
    case EU_STATUS_BUFFER_TOO_SMALL:
        return "buffer_too_small";
    case EU_STATUS_NOT_FOUND:
        return "not_found";
    case EU_STATUS_INVALID_ARGUMENT:
        return "invalid_argument";
    case EU_STATUS_BOUNDARY_VIOLATION:
        return "boundary_violation";
    default:
        break;
    }
    return "unknown";
}
