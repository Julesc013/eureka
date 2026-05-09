#ifndef EU_WIN32_SNAPSHOT_ADAPTER_H
#define EU_WIN32_SNAPSHOT_ADAPTER_H

#ifdef __cplusplus
extern "C" {
#endif

int eu_win32_snapshot_adapter_has_manifest(const char *text);
const char *eu_win32_snapshot_adapter_summary(void);

#ifdef __cplusplus
}
#endif

#endif
