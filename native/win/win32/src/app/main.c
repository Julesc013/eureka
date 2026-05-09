#include <windows.h>
#include "eu_win32_app.h"

int WINAPI WinMain(HINSTANCE instance_handle, HINSTANCE previous_instance, LPSTR command_line, int show_command)
{
    (void)previous_instance;
    (void)command_line;
    return eu_win32_run(instance_handle, show_command);
}
