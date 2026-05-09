#include "eu_relay.h"
#include "eu_string.h"

int eu_relay_status_is_readonly(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "read_only")) {
        return 1;
    }
    return eu_contains_token(text, text_len, "localhost_readonly");
}

int eu_relay_status_is_loopback_only(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "localhost_only")) {
        return 1;
    }
    if (eu_contains_token(text, text_len, "127.0.0.1")) {
        return 1;
    }
    return eu_contains_token(text, text_len, "localhost");
}

int eu_relay_status_blocks_live_access(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "live_access_enabled") &&
        eu_contains_token(text, text_len, "false")) {
        return 1;
    }
    return eu_contains_token(text, text_len, "no_live_access");
}

eu_status_code eu_relay_status_from_text(const char *text, size_t text_len, char *dest, size_t dest_size)
{
    if (text == 0 || dest == 0) {
        return EU_STATUS_NULL_ARGUMENT;
    }
    if (eu_contains_token(text, text_len, "localhost_readonly")) {
        return eu_copy_string(dest, dest_size, "localhost_readonly");
    }
    if (eu_contains_token(text, text_len, "fixture_only")) {
        return eu_copy_string(dest, dest_size, "fixture_only");
    }
    if (dest_size > 0) {
        dest[0] = '\0';
    }
    return EU_STATUS_NOT_FOUND;
}
