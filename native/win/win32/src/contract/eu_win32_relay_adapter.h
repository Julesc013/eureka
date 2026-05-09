#ifndef EU_WIN32_RELAY_ADAPTER_H
#define EU_WIN32_RELAY_ADAPTER_H

#ifdef __cplusplus
extern "C" {
#endif

int eu_win32_relay_adapter_is_readonly(const char *text);
const char *eu_win32_relay_adapter_summary(void);

#ifdef __cplusplus
}
#endif

#endif
