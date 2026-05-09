#ifndef EU_WIN32_APP_H
#define EU_WIN32_APP_H

#include <windows.h>

#ifdef __cplusplus
extern "C" {
#endif

int eu_win32_run(HINSTANCE instance_handle, int show_command);
const char *eu_win32_scope_text(void);

#ifdef __cplusplus
}
#endif

#endif
