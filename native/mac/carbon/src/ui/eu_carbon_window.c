#include "eu_carbon_window.h"
#include "../app/eu_carbon_app.h"
#include "../contract/eu_carbon_snapshot_adapter.h"
#include "../contract/eu_carbon_relay_adapter.h"

void eu_carbon_show_window(void)
{
    (void)eu_carbon_scope_text();
    (void)eu_carbon_snapshot_adapter_summary();
    (void)eu_carbon_relay_adapter_summary();
}

const char *eu_carbon_window_summary(void)
{
    return "Carbon window placeholder with search, object, relay, blocked action, and diagnostics panes.";
}
