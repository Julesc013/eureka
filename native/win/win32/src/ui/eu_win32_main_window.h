#ifndef EU_WIN32_MAIN_WINDOW_H
#define EU_WIN32_MAIN_WINDOW_H

#include <windows.h>

#ifdef __cplusplus
extern "C" {
#endif

int eu_win32_register_main_window(HINSTANCE instance_handle);
HWND eu_win32_create_main_window(HINSTANCE instance_handle);

#ifdef __cplusplus
}
#endif

#endif
