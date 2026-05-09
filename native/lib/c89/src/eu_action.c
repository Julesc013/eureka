#include "eu_action.h"
#include "eu_string.h"

int eu_action_manifest_is_safe_current(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "view")) {
        return 1;
    }
    if (eu_contains_token(text, text_len, "inspect")) {
        return 1;
    }
    if (eu_contains_token(text, text_len, "cite")) {
        return 1;
    }
    return eu_contains_token(text, text_len, "blocked_action");
}

int eu_action_manifest_is_blocked(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "blocked_action")) {
        return 1;
    }
    return eu_contains_token(text, text_len, "blocked_reason");
}

int eu_action_manifest_blocks_execution(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "action_manifest_executes_action") &&
        eu_contains_token(text, text_len, "false")) {
        return 1;
    }
    if (eu_contains_token(text, text_len, "execute") &&
        eu_contains_token(text, text_len, "blocked")) {
        return 1;
    }
    return 0;
}

eu_status_code eu_action_family_from_text(const char *text, size_t text_len, char *dest, size_t dest_size)
{
    if (text == 0 || dest == 0) {
        return EU_STATUS_NULL_ARGUMENT;
    }
    if (eu_contains_token(text, text_len, "blocked_action")) {
        return eu_copy_string(dest, dest_size, "blocked_action");
    }
    if (eu_contains_token(text, text_len, "acquisition_manifest")) {
        return eu_copy_string(dest, dest_size, "acquisition_manifest");
    }
    if (eu_contains_token(text, text_len, "cite")) {
        return eu_copy_string(dest, dest_size, "cite");
    }
    if (eu_contains_token(text, text_len, "view")) {
        return eu_copy_string(dest, dest_size, "view");
    }
    if (dest_size > 0) {
        dest[0] = '\0';
    }
    return EU_STATUS_NOT_FOUND;
}
