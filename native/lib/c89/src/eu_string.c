#include "eu_string.h"

size_t eu_strnlen_c89(const char *text, size_t max_len)
{
    size_t index;

    if (text == 0) {
        return 0;
    }
    index = 0;
    while (index < max_len && text[index] != '\0') {
        index = index + 1;
    }
    return index;
}

int eu_contains_token(const char *text, size_t text_len, const char *token)
{
    size_t token_len;
    size_t i;
    size_t j;
    int matched;

    if (text == 0 || token == 0) {
        return 0;
    }
    token_len = eu_strnlen_c89(token, 256);
    if (token_len == 0 || token_len > text_len) {
        return 0;
    }
    i = 0;
    while (i + token_len <= text_len) {
        matched = 1;
        j = 0;
        while (j < token_len) {
            if (text[i + j] != token[j]) {
                matched = 0;
                break;
            }
            j = j + 1;
        }
        if (matched) {
            return 1;
        }
        i = i + 1;
    }
    return 0;
}

eu_status_code eu_copy_string(char *dest, size_t dest_size, const char *src)
{
    size_t len;
    size_t i;

    if (dest == 0 || src == 0) {
        return EU_STATUS_NULL_ARGUMENT;
    }
    if (dest_size == 0) {
        return EU_STATUS_BUFFER_TOO_SMALL;
    }
    len = eu_strnlen_c89(src, dest_size);
    if (len >= dest_size) {
        dest[0] = '\0';
        return EU_STATUS_BUFFER_TOO_SMALL;
    }
    i = 0;
    while (i < len) {
        dest[i] = src[i];
        i = i + 1;
    }
    dest[len] = '\0';
    return EU_STATUS_OK;
}
