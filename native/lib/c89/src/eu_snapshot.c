#include "eu_snapshot.h"
#include "eu_string.h"

int eu_snapshot_has_manifest_marker(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "snapshot_manifest")) {
        return 1;
    }
    return eu_contains_token(text, text_len, "snapshot_manifest_id");
}

int eu_snapshot_has_record_marker(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "snapshot_record")) {
        return 1;
    }
    return eu_contains_token(text, text_len, "record_type");
}

int eu_snapshot_has_no_claims_marker(const char *text, size_t text_len)
{
    if (eu_contains_token(text, text_len, "no_claims")) {
        return 1;
    }
    return eu_contains_token(text, text_len, "limitations");
}

eu_status_code eu_snapshot_status_from_text(const char *text, size_t text_len, char *dest, size_t dest_size)
{
    if (text == 0 || dest == 0) {
        return EU_STATUS_NULL_ARGUMENT;
    }
    if (eu_contains_token(text, text_len, "verified_local")) {
        return eu_copy_string(dest, dest_size, "verified_local");
    }
    if (eu_contains_token(text, text_len, "fixture_only")) {
        return eu_copy_string(dest, dest_size, "fixture_only");
    }
    if (eu_contains_token(text, text_len, "example_only")) {
        return eu_copy_string(dest, dest_size, "example_only");
    }
    if (dest_size > 0) {
        dest[0] = '\0';
    }
    return EU_STATUS_NOT_FOUND;
}
