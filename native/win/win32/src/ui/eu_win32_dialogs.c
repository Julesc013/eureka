#include "eu_win32_dialogs.h"

void eu_win32_show_about(HWND owner)
{
    MessageBoxA(
        owner,
        "Eureka Win32 read-only skeleton\nBuild evidence is manual and unverified.\nNo live access or risky actions are enabled.",
        "Eureka",
        MB_OK | MB_ICONINFORMATION);
}
