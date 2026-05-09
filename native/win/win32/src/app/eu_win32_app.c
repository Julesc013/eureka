#include "eu_win32_app.h"
#include "../ui/eu_win32_main_window.h"

int eu_win32_run(HINSTANCE instance_handle, int show_command)
{
    HWND window_handle;
    MSG message;
    int class_status;

    class_status = eu_win32_register_main_window(instance_handle);
    if (class_status == 0) {
        return 1;
    }
    window_handle = eu_win32_create_main_window(instance_handle);
    if (window_handle == 0) {
        return 1;
    }
    ShowWindow(window_handle, show_command);
    UpdateWindow(window_handle);
    while (GetMessageA(&message, 0, 0, 0) > 0) {
        TranslateMessage(&message);
        DispatchMessageA(&message);
    }
    return (int)message.wParam;
}

const char *eu_win32_scope_text(void)
{
    return "Read-only fixture viewer over snapshot, relay, and action contracts.";
}
