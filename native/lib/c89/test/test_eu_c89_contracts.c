#include <stddef.h>
#include "eu_status.h"
#include "eu_string.h"
#include "eu_snapshot.h"
#include "eu_relay.h"
#include "eu_action.h"

static int require_true(int value)
{
    if (value) {
        return 0;
    }
    return 1;
}

int main(void)
{
    const char *snapshot_text;
    const char *relay_text;
    const char *action_text;
    char buffer[32];
    eu_status_code status;
    int failures;

    snapshot_text = "{\"schema_version\":\"snapshot_manifest.v0\",\"manifest_status\":\"fixture_only\",\"no_claims\":[]}";
    relay_text = "{\"relay_mode\":\"localhost_readonly\",\"localhost_only\":true,\"read_only\":true,\"live_access_enabled\":false}";
    action_text = "{\"action_family\":\"blocked_action\",\"blocked_reason\":\"execute disabled\",\"action_manifest_executes_action\":false}";
    failures = 0;

    failures = failures + require_true(eu_status_is_ok(EU_STATUS_OK));
    failures = failures + require_true(eu_contains_token(snapshot_text, eu_strnlen_c89(snapshot_text, 512), "snapshot_manifest"));
    failures = failures + require_true(eu_snapshot_has_manifest_marker(snapshot_text, eu_strnlen_c89(snapshot_text, 512)));
    failures = failures + require_true(eu_snapshot_has_no_claims_marker(snapshot_text, eu_strnlen_c89(snapshot_text, 512)));
    failures = failures + require_true(eu_relay_status_is_readonly(relay_text, eu_strnlen_c89(relay_text, 512)));
    failures = failures + require_true(eu_relay_status_is_loopback_only(relay_text, eu_strnlen_c89(relay_text, 512)));
    failures = failures + require_true(eu_relay_status_blocks_live_access(relay_text, eu_strnlen_c89(relay_text, 512)));
    failures = failures + require_true(eu_action_manifest_is_blocked(action_text, eu_strnlen_c89(action_text, 512)));
    failures = failures + require_true(eu_action_manifest_blocks_execution(action_text, eu_strnlen_c89(action_text, 512)));

    status = eu_snapshot_status_from_text(snapshot_text, eu_strnlen_c89(snapshot_text, 512), buffer, sizeof(buffer));
    failures = failures + require_true(status == EU_STATUS_OK);
    failures = failures + require_true(eu_contains_token(buffer, eu_strnlen_c89(buffer, 32), "fixture_only"));

    return failures;
}
