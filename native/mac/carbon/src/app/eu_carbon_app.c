#include "eu_carbon_app.h"
#include "../ui/eu_carbon_window.h"

int eu_carbon_run(void)
{
    eu_carbon_show_window();
    return 0;
}

const char *eu_carbon_scope_text(void)
{
    return "Read-only fixture viewer over snapshot, relay, and action contracts.";
}
