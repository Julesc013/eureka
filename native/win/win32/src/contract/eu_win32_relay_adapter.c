#include "eu_win32_relay_adapter.h"
#include <string.h>

int eu_win32_relay_adapter_is_readonly(const char *text)
{
    if (text == 0) {
        return 0;
    }
    if (strstr(text, "localhost_readonly") != 0) {
        return 1;
    }
    return strstr(text, "read_only") != 0;
}

const char *eu_win32_relay_adapter_summary(void)
{
    return "Relay: localhost/read-only fixture status display only.";
}
