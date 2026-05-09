#include "eu_win32_main_window.h"
#include "eu_win32_dialogs.h"
#include "../app/eu_win32_app.h"
#include "../contract/eu_win32_snapshot_adapter.h"
#include "../contract/eu_win32_relay_adapter.h"
#include "../../res/resource.h"

static const char *EU_WIN32_CLASS_NAME = "EurekaWin32ReadOnlyWindow";

static LRESULT CALLBACK eu_win32_window_proc(HWND window_handle, UINT message, WPARAM wparam, LPARAM lparam);
static void eu_win32_paint(HWND window_handle);

int eu_win32_register_main_window(HINSTANCE instance_handle)
{
    WNDCLASSA window_class;

    ZeroMemory(&window_class, sizeof(window_class));
    window_class.style = CS_HREDRAW | CS_VREDRAW;
    window_class.lpfnWndProc = eu_win32_window_proc;
    window_class.hInstance = instance_handle;
    window_class.hIcon = LoadIconA(0, IDI_APPLICATION);
    window_class.hCursor = LoadCursorA(0, IDC_ARROW);
    window_class.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    window_class.lpszMenuName = MAKEINTRESOURCEA(IDR_EUREKA_MENU);
    window_class.lpszClassName = EU_WIN32_CLASS_NAME;
    return RegisterClassA(&window_class) != 0;
}

HWND eu_win32_create_main_window(HINSTANCE instance_handle)
{
    return CreateWindowExA(
        0,
        EU_WIN32_CLASS_NAME,
        "Eureka Win32 Read-Only Skeleton",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        760,
        520,
        0,
        0,
        instance_handle,
        0);
}

static LRESULT CALLBACK eu_win32_window_proc(HWND window_handle, UINT message, WPARAM wparam, LPARAM lparam)
{
    switch (message) {
    case WM_COMMAND:
        if (LOWORD(wparam) == IDM_EUREKA_ABOUT) {
            eu_win32_show_about(window_handle);
            return 0;
        }
        if (LOWORD(wparam) == IDM_EUREKA_EXIT) {
            DestroyWindow(window_handle);
            return 0;
        }
        break;
    case WM_PAINT:
        eu_win32_paint(window_handle);
        return 0;
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    default:
        break;
    }
    return DefWindowProcA(window_handle, message, wparam, lparam);
}

static void eu_win32_paint(HWND window_handle)
{
    PAINTSTRUCT paint;
    HDC dc;
    int y;

    dc = BeginPaint(window_handle, &paint);
    y = 24;
    TextOutA(dc, 24, y, "Eureka Win32 ANSI skeleton", 27);
    y = y + 28;
    TextOutA(dc, 24, y, eu_win32_scope_text(), lstrlenA(eu_win32_scope_text()));
    y = y + 32;
    TextOutA(dc, 24, y, "Search: fixture result list placeholder", 39);
    y = y + 24;
    TextOutA(dc, 24, y, "Object/source summary: local contract text only", 47);
    y = y + 24;
    TextOutA(dc, 24, y, eu_win32_snapshot_adapter_summary(), lstrlenA(eu_win32_snapshot_adapter_summary()));
    y = y + 24;
    TextOutA(dc, 24, y, eu_win32_relay_adapter_summary(), lstrlenA(eu_win32_relay_adapter_summary()));
    y = y + 24;
    TextOutA(dc, 24, y, "Blocked actions: download, install, execute, emulate", 52);
    y = y + 24;
    TextOutA(dc, 24, y, "No rights, safety, installability, or truth acceptance claims.", 61);
    EndPaint(window_handle, &paint);
}
