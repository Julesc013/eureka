#include "eu_carbon_snapshot_adapter.h"
#include <string.h>

int eu_carbon_snapshot_adapter_has_manifest(const char *text)
{
    if (text == 0) {
        return 0;
    }
    if (strstr(text, "snapshot_manifest") != 0) {
        return 1;
    }
    return strstr(text, "snapshot_record") != 0;
}

const char *eu_carbon_snapshot_adapter_summary(void)
{
    return "Snapshot: local manifest/record fixture text, read-only.";
}
